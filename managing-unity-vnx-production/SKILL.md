---
name: managing-unity-vnx-production
description: Use when inspecting, troubleshooting, or changing Dell Unity, Unity XT or VNX (VNX1/VNX2 block and file) arrays, especially production arrays with critical data - uemcli, naviseccli, Unisphere, pools, LUNs, storage groups, hosts, snapshots, trespass, SP ownership, NAS servers, Data Movers, replication, MirrorView, capacity.
---

# Managing Unity / VNX in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Unity reads:** the community Unity MCP server (GET-only), or `uemcli ... show`. It needs a dedicated **Operator-role** (read-only) account, because the MCP passes the password on every call. Never enable write methods on it.
- **VNX reads:** `naviseccli` (block) and `nas_*`/`server_*` list commands (file), run as a read-only account.
- Cite the array and timestamp for every value. If a tool fails, say so. Never guess state. Details: references/access-and-tools.md.
- **Writes:** only the commands in an approved plan, one per step, with a read after each. An admin identity is used only by the human, only for the approved window.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | show/list/getagent/getlog/faults, MCP GETs | none |
| T1 additive | snapshot/checkpoint, create LUN/FS/share/host, access to a new LUN, spcollect | plan + "approve" |
| T2 modify | expand LUN/FS/pool, schedules, auto-delete thresholds, host I/O limits, replication pause/resume, trespass to default owner | full plan + "approve" per T2 item |
| T3 destructive/disruptive | delete snapshot/LUN/FS/datastore/NAS server, snapshot restore/rollback, remove host access/initiator/storage-group member, replication failover/fracture/promote, Data Mover failover, SP reboot, NDU/OE upgrade | full plan + user types object name; safety snapshot first |

## Narrowest option first
- Pool full: read where the space goes → auto-delete thresholds → expand pool → delete **named** snapshots.
- SP reboot / trespass: root cause and SP health first → verify host paths → trespass back. NDU is a separate T3 change.
- Restore: attach/mount the snapshot and copy → restore last.

## Facts not to get wrong
- At 100% pool used, thin resources stop taking writes, and datastores and VMs pause.
- Snapshot restore overwrites newer data. Keep a backup snapshot.
- Don't delete attached, replication-owned or app-created (AppSync/RecoverPoint/backup) snapshots.
- An NDU reboots each SP in turn. VNX is end of life, so check the support status before any upgrade or parts action.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said don't list them / just clean up" | Show a compact list anyway. Approval covers the listed IDs only. |
| "Reply go and I'll delete the safe set" | The user can't approve objects they never saw. |
| "Admin creds are already saved, reads are harmless" | Use the read-only account. Admin is for approved changes only. |
| "P1 / I'm the lead, just do it" | Approval before the plan existed approves nothing. Use the terse emergency plan. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/unity.md: Unity objects, commands by tier, pool-full relief
- references/vnx.md: VNX block and file objects, commands by tier
- references/access-and-tools.md: Unity MCP setup and risks, uemcli/naviseccli credentials
- references/health-and-triage.md: health report, incident playbooks
