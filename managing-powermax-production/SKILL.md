---
name: managing-powermax-production
description: Use when inspecting, troubleshooting, or changing Dell PowerMax or VMAX (VMAX3, VMAX All Flash, VMAX 10K/20K/40K) arrays, especially production arrays with critical data - symcli, Solutions Enabler, Unisphere for PowerMax, storage groups, masking views, devices, SnapVX, SRDF, SRP capacity, latency, upgrades, migration, best practices, configuration audit.
---

# Managing PowerMax / VMAX in Production

## Overview
Reading is free; changing is gated. Every change above read-only is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Reads:** read-only symcli (`list`, `show`, `query`, `verify`, `symevent`, `symaudit`, `symstat`) as a **Monitor-role** identity. Always pass `-sid`. Cite SID and timestamp. If the CLI fails, say so. Never guess state.
- **No production-grade MCP exists** for PowerMax/VMAX. Don't use experimental servers on production.
- **Writes:** only approved plan commands, one per step, a read after each, prompts on (never `-noprompt`/`-force`/`-symforce`).

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | list/show/query/verify, events, audit, stats, `symaccess backup` | none |
| T1 additive | SnapVX with TTL, create dev/SG/MV, add dev to SG, link to new empty targets | plan + "approve" |
| T2 modify | expand dev, SL/host I/O limits, SRDF resume/incremental establish/suspend/split, add initiator | plan + "approve" per item |
| T3 destructive/disruptive | delete MV, remove dev/initiator/port, free/delete devices, SnapVX restore/terminate/link -copy onto data, secure snaps, SRDF `-full`/failover/swap/deletepair, code/director changes | plan + typed object name; snapshot first |

## Narrowest option first
- Decommission: unmask → quarantine (default 7 days) → separate approval to deallocate.
- SRDF resync: gold-copy SnapVX of R2 → `resume`/incremental establish → `-full` only if track tables are invalid.
- Restore: link the snapshot to new targets → copy → SnapVX `restore` last.

## Facts not to get wrong
- `free -all` / delete = data gone, and its snapshots too.
- During a resync R2 is **inconsistent**: no restartable DR image without a gold copy.
- Devices can sit in several (cascaded) SGs and MVs. Check `symdev show` for each.
- A minute of zero I/O is not proof of disuse.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said do it now / I'm the lead" | Approval before the plan existed approves nothing. |
| "Safety snapshot is optional" | Step 0 of every T3. Skip only with a stated reason. |
| "Unmask and deallocate together saves time" | Unmask is reversible, deallocate isn't. Separate approvals. |
| "`-full` is the thorough fix" | Slower, and DR is unprotected throughout. |

## References
- change-gate.md: plan template, **required for any change**
- best-practices.md: configuration audit
- powermax-vmax.md: objects, commands by tier, decommission, SRDF recovery
- access-and-tools.md: read-only identity, symcli whitelist, credentials
- health-and-triage.md: health report, playbooks
- incident-comms.md: status updates, postmortem
- upgrade-checklist.md / upgrades-and-migration.md: code upgrades, NDM, tech refresh
