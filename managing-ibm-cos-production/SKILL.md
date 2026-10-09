---
name: managing-ibm-cos-production
description: Use when inspecting, troubleshooting, or changing IBM Cloud Object Storage on-premises (Cleversafe, dsNet, ClevOS) systems, especially production systems with critical data - Manager, Accessers, Slicestors, device sets, storage pools, vaults, containers, IDA width and thresholds, firmware upgrades, drive failures, rebuilder, retention vaults, legal holds, access keys, S3, best practices, configuration audit.
---

# Managing IBM COS (Cleversafe) in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **No MCP server exists** for on-prem dsNet. The IBM Cloud COS servers don't fit. Claude reads through its shell: Manager REST API `view*`/`list*` as a **Read Only** role user, and `aws s3api get-*`/`head-*` with a config-only profile. Cite device or vault and timestamp. Never guess state. Details: references/access-and-tools.md.
- **Never use the Super User account for reads**, even if it's saved. Never print passwords or keys.
- **Writes:** only the calls in an approved plan, one per step, with a read of device and vault health after each.

## IDA math before touching any device
Margin = available devices in the set − write threshold, for **every vault** on the set. Count devices that are already down, degraded or under RMA first. Max devices offline at once = margin − 1. Below the write threshold, writes fail. Below the read threshold, data is unavailable.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | Manager view/list, s3api get/head, bounded list | none |
| T1 additive | create vault/user/key, second access key, time-boxed alert mute | plan + "approve" |
| T2 modify | quota, ACL/policy, versioning, template, single-device maintenance/reboot/firmware within the margin, mark a drive failed | full plan + "approve" per T2 item |
| T3 destructive/irreversible | several devices at once, remove/replace device, delete/empty vault, lifecycle expiration, retention/legal hold/Object Lock, delete key/user, break mirror, remove Accesser/proxy, ClevOS upgrade | full plan + user types object name; owner sign-off |

## Narrowest option first
- Upgrades: one device at a time, waiting for full health and the rebuilder between devices.
- Noisy drives: drive-level action, not node removal.
- Vault deletion: remove it from its access pool (reversible cool-off), then delete it with a separate approval.

## Facts not to get wrong
- Retention can't be disabled. Nobody, including Super User, deletes objects under retention early.
- IDA and storage pool are fixed at vault creation.
- Don't stack maintenance on a set that is rebuilding.

## Rationalizations
| Thought | Reality |
|---|---|
| "Super User is already saved, reads are harmless" | Use the Read Only account. Super User is never for reads. |
| "Four at a time is faster" | Do the math with the devices already down. Never go past margin − 1. |
| "Remove the node to stop alerts" | Mute the alerts for a set time or fail the drive. Removing the node reduces the margin. |
| "Legal approved, force it" | WORM can't be bypassed. Report expiry and holds, and escalate to legal. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/best-practices.md: recommended configuration, read-only audit checks and fix tiers (use for best-practice or config reviews)
- references/ibm-cos.md: IDA math, objects, tiers, rolling maintenance, retention/GDPR
- references/access-and-tools.md: Read Only identities, Manager API, secrets
- references/health-and-triage.md: health report, incident playbooks
