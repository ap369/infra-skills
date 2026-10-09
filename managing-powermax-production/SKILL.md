---
name: managing-powermax-production
description: Use when inspecting, troubleshooting, or changing Dell PowerMax or VMAX (VMAX3, VMAX All Flash, VMAX 10K/20K/40K) arrays, especially production arrays with critical data - symcli, Solutions Enabler, Unisphere for PowerMax, storage groups, masking views, devices, SnapVX, SRDF, SRP capacity, latency, best practices, configuration audit.
---

# Managing PowerMax / VMAX in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Reads:** Claude runs read-only symcli (`list`, `show`, `query`, `verify`, `symevent`, `symaudit`, `symstat`) on the management host, as a **Monitor-role** identity. Always pass `-sid`. Cite SID and timestamp. If the CLI fails, say so. Never guess state. Details: references/access-and-tools.md.
- **No production-grade MCP exists** for PowerMax/VMAX. Don't use experimental servers against production.
- **Writes:** only the commands in an approved plan, one per step, a read after each, prompts left on (never `-noprompt`/`-force`/`-symforce`).

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | list/show/query/verify, events, audit, stats, `symaccess backup` | none |
| T1 additive | SnapVX snapshot with TTL, create dev/SG/MV, add dev to SG, link to new empty targets | plan + "approve" |
| T2 modify | expand dev, SL/host I/O limits, SRDF resume/incremental establish/suspend/split, add initiator | full plan + "approve" per T2 item |
| T3 destructive/disruptive | delete MV, remove dev/initiator/port, free/delete devices, SnapVX restore/terminate/link -copy onto data, secure snaps, SRDF `-full`/failover/swap/deletepair, code/director changes | full plan + user types object name; safety snapshot first |

## Narrowest option first
- Decommission: unmask → quarantine (default 7 days) → separate approval to deallocate.
- SRDF resync: gold-copy SnapVX of R2 → `resume`/incremental establish → `-full` only if the track tables are invalid.
- Restore: link the snapshot to new targets → copy data → SnapVX `restore` last.

## Facts not to get wrong
- `free -all` / delete = data gone. Snapshots of deleted devices go too.
- During a resync R2 is **inconsistent**: no restartable DR image without a gold copy.
- Devices can sit in several SGs and MVs (cascaded). Check `symdev show` for each device.
- Zero I/O for a minute is not proof of disuse.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said do it now / I'm the lead" | Approval before the plan existed approves nothing. Write a short plan. |
| "Safety snapshot is optional" | Step 0 of every T3. Skip only with a stated reason. |
| "Unmask and deallocate together saves time" | Unmask is reversible, deallocate isn't. Separate approvals with a quarantine. |
| "`-full` is the thorough fix" | Slower, and DR is unprotected throughout. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/best-practices.md: recommended configuration, read-only audit checks and fix tiers (use for best-practice or config reviews)
- references/powermax-vmax.md: objects, commands by tier, pre-checks, decommission, SRDF recovery
- references/access-and-tools.md: read-only identity, symcli whitelist, REST, credentials
- references/health-and-triage.md: health report, incident playbooks
