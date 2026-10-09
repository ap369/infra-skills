---
name: managing-unity-vnx-production
description: Use when inspecting, troubleshooting, or changing Dell Unity, Unity XT or VNX (VNX1/VNX2 block and file) arrays, especially production arrays with critical data - uemcli, naviseccli, Unisphere, pools, LUNs, storage groups, hosts, snapshots, trespass, SP ownership, NAS servers, Data Movers, replication, MirrorView, capacity, upgrades, VNX migration, best practices, configuration audit.
---

# Managing Unity / VNX in Production

## Overview
Reading is free; changing is gated. Every change above read-only is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Unity reads:** the community Unity MCP server (GET-only) or `uemcli ... show`, as a dedicated **Operator** (read-only) account, because the MCP passes the password on every call. Never enable write methods.
- **VNX reads:** `naviseccli` and `nas_*`/`server_*` list commands as a read-only account.
- Cite array and timestamp. Never guess state. **Writes:** approved plan commands only, one per step; admin identity only by the human, for the window.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | show/list/getagent/getlog/faults, MCP GETs | none |
| T1 additive | snapshot/checkpoint, create LUN/FS/share/host, access to a new LUN, spcollect | plan + "approve" |
| T2 modify | expand LUN/FS/pool, schedules, auto-delete thresholds, host I/O limits, replication pause/resume, trespass to default owner | plan + "approve" per item |
| T3 destructive/disruptive | delete snapshot/LUN/FS/datastore/NAS server, snapshot restore/rollback, remove host access/initiator, replication failover/fracture/promote, Data Mover failover, SP reboot, NDU | plan + typed object name; snapshot first |

## Narrowest option first
- Pool full: read where the space goes → auto-delete thresholds → expand → delete **named** snapshots.
- SP reboot / trespass: root cause and SP health → host paths → trespass back. NDU is a separate change.
- Restore: attach/mount the snapshot and copy → restore last.

## Facts not to get wrong
- At 100% pool, thin resources stop taking writes; datastores and VMs pause.
- Snapshot restore overwrites newer data. Keep a backup snapshot.
- Never delete attached, replication-owned or app-created (AppSync/RecoverPoint/backup) snapshots.
- VNX is end of life: check support status before any upgrade or parts action; plan migration.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said don't list them / just clean up" | Show a compact list anyway; approval covers listed IDs only. |
| "Reply go and I'll delete the safe set" | The user can't approve objects they never saw. |
| "Admin creds are saved, reads are harmless" | Use the read-only account. |
| "P1 / I'm the lead, just do it" | Approval before the plan existed approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- best-practices.md: configuration audit
- unity.md / vnx.md: objects, commands by tier, pool-full relief, decommission
- access-and-tools.md: Unity MCP risks, uemcli/naviseccli credentials
- health-and-triage.md: health report, playbooks
- incident-comms.md: status updates, postmortem
- upgrade-checklist.md / upgrades-and-migration.md: OE upgrades, VNX exit
