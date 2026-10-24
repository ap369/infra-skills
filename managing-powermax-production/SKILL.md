---
name: managing-powermax-production
description: Use when inspecting, troubleshooting, or changing Dell PowerMax or VMAX (VMAX3, VMAX All Flash, VMAX 10K/20K/40K) arrays, especially production arrays with critical data - symcli, Solutions Enabler, Unisphere for PowerMax, storage groups, masking views, devices, SnapVX, SRDF, SRP capacity, latency, upgrades, migration, best practices, configuration audit, REST API, Python.
---

# Managing PowerMax / VMAX in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Reads:** read-only symcli (`list`, `show`, `query`, `verify`, `symevent`, `symaudit`, `symstat`) as a **Monitor-role** identity. Always pass `-sid`. Cite SID and timestamp; if the CLI fails, say so; never guess.
- **No production-grade MCP exists** for PowerMax/VMAX. Don't use experimental ones on production.
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
- Restore: link snapshot to new targets → copy → `restore` last.

## Key facts
- `free -all` / delete = data gone, and its snapshots too.
- During a resync R2 is **inconsistent**: no restartable image without a gold copy. `-full` is for initial sync or R2 drive swap only.
- Devices can sit in several (cascaded) SGs/MVs: check `symdev show`.
- A minute of zero I/O is not proof of disuse.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this command/flag exists" | Prove it: `[doc]` or help output this session. Otherwise `[unverified]`, never a plan step. |
| "User said do it now / I'm the lead" | Approval before the plan existed approves nothing. |
| "Safety snapshot is optional" | Step 0 of every T3. Skip only with a stated reason. |
| "Unmask and deallocate together saves time" | Unmask is reversible, deallocate isn't. Separate approvals. |
| "`-full` is the thorough fix" | Slower; DR is unprotected throughout. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md: source tags, **required**; symcli-command-catalog.md: [doc] forms
- snapvx-and-srdf.md / powermax-security-and-versions.md: Dell docs
- best-practices.md: configuration audit
- powermax-vmax.md: objects, tiers, decommission, SRDF recovery
- access-and-tools.md: read-only identity, credentials
- health-and-triage.md / incident-comms.md: health, playbooks, status updates
- upgrade-checklist.md / upgrades-and-migration.md: code upgrades, NDM, tech refresh
- powermax-api/: Unisphere REST API, Python
