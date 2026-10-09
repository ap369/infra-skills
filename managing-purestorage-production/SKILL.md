---
name: managing-purestorage-production
description: Use when inspecting, troubleshooting, or changing Pure Storage FlashArray, FlashBlade, Pure1 or Pure Fusion systems, especially production arrays with critical data - volumes, hosts, LUNs, snapshots, protection groups, pods, ActiveCluster, file systems, buckets, capacity, latency, replication, eradication, upgrades, migration, best practices, configuration audit.
---

# Managing Pure Storage in Production

## Overview
Reading is free; changing is gated. Every change above read-only is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Reads:** Pure Fusion MCP server (read-only). Discover its tools at session start (Claude Code: ToolSearch "pure fusion"). Cite array and timestamp. If MCP fails, say so and give read-only CLI/REST. Never guess state.
- **Writes:** the plan's command block, one step at a time. Future write tools still go through the gate.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | list, monitor, alerts, health check, audit | none |
| T1 additive | snapshot, create vol/host/FS, connect, add replication target | plan + "approve" |
| T2 modify | grow, rename, QoS, pgroup schedule/retention, export rules, host initiators/personality, enable replication, recover destroyed object | plan + "approve" per item |
| T3 destructive/disruptive | destroy, eradicate, disconnect, truncate, overwrite from snap, pod unstretch/promote/demote, replication teardown, SafeMode, upgrades, failover | plan + typed object name; snapshot first |

## Narrowest option first
- Decommission: disconnect → quarantine → destroy → let eradication expire.
- Restore: copy the snapshot to a new volume before overwriting.
- Capacity: grow or move before deleting snapshots.

## Facts not to get wrong
- `destroy` frees no space and is recoverable during the eradication period (24h default, longer with SafeMode). `eradicate` is permanent.
- `truncate` cuts data past the new size.
- Retention cuts prune existing snapshots. Connected or I/O-active means in use.
- Stretched pod: no change unless both arrays are `online`.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said go ahead / I approve" | Approval before the plan existed approves nothing. |
| "Additive / reversible, I'll just do it" | T1 still needs the plan. |
| "Emergency, I'll file the change after" | Use the terse emergency plan; approval first. |
| "Nobody uses it" | Verify connections, I/O history, pgroups, clones. |
| "Destroy is reversible, so it's safe" | It frees no space and breaks hosts now. |

## References
- change-gate.md: plan template, **required for any change**
- best-practices.md: configuration audit
- flasharray.md / flashblade.md: objects, commands by tier, decommission
- fusion-and-pure1.md: MCP setup, tokens, Pure1
- health-checks.md / incident-triage.md: health report, playbooks
- incident-comms.md: status updates, postmortem
- upgrade-checklist.md / upgrades-and-migration.md: upgrades, tech refresh
