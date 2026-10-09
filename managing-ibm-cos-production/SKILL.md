---
name: managing-ibm-cos-production
description: Use when inspecting, troubleshooting, or changing IBM Cloud Object Storage on-premises (Cleversafe, dsNet, ClevOS) systems, especially production systems with critical data - Manager, Accessers, Slicestors, device sets, vaults, IDA width and thresholds, firmware upgrades, drive failures, rebuilder, retention vaults, legal holds, access keys, S3, migration, best practices, configuration audit.
---

# Managing IBM COS (Cleversafe) in Production

## Overview
Reading is free; changing is gated. Every change above read-only is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **No MCP server exists** for on-prem dsNet. Read via shell: Manager `view*`/`list*` as a **Read Only** user, `aws s3api get-*`/`head-*` with a config-only profile. Cite device/vault and timestamp. Never guess state.
- **Never use Super User for reads**, even if saved. Never print passwords or keys.
- **Writes:** approved plan calls only, one per step, re-reading health after each.

## IDA math before touching any device
Margin = available devices − write threshold, for **every vault** on the set, counting devices already down. Max offline at once = margin − 1. Below write threshold writes fail; below read threshold data is unavailable.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | Manager view/list, s3api get/head, bounded list | none |
| T1 additive | create vault/user/key, second access key, time-boxed alert mute | plan + "approve" |
| T2 modify | quota, ACL/policy, versioning, template, single-device maintenance/firmware within margin, mark drive failed | plan + "approve" per item |
| T3 destructive/irreversible | several devices at once, remove/replace device, delete/empty vault, lifecycle expiration, retention/legal hold/Object Lock, delete key/user, break mirror, remove Accesser/proxy, ClevOS upgrade | plan + typed object name; owner sign-off |

## Narrowest option first
- Upgrades: one device at a time, healthy between devices.
- Noisy drives: drive-level action, not node removal.
- Vault deletion: access-pool removal (cool-off) → delete with a separate approval.

## Facts not to get wrong
- Retention can't be disabled; nobody, Super User included, deletes retained objects early.
- IDA and storage pool are fixed at vault creation.
- Don't stack maintenance on a rebuilding set.

## Rationalizations
| Thought | Reality |
|---|---|
| "Super User is saved, reads are harmless" | Use Read Only. Super User is never for reads. |
| "Four at a time is faster" | Do the math with devices already down; never past margin − 1. |
| "Remove the node to stop alerts" | Time-boxed mute or fail the drive; removal cuts the margin. |
| "Legal approved, force it" | WORM can't be bypassed. Report expiry/holds; escalate to legal. |

## References
- change-gate.md: plan template, **required for any change**
- best-practices.md: configuration audit
- ibm-cos.md: IDA, objects, tiers, maintenance, retention
- access-and-tools.md: Read Only identities, Manager API, secrets
- health-and-triage.md: health report, playbooks
- incident-comms.md: status updates, postmortem
- upgrade-checklist.md / upgrades-and-migration.md: ClevOS upgrades, migration
