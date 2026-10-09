---
name: managing-purestorage-production
description: Use when inspecting, troubleshooting, or changing Pure Storage FlashArray, FlashBlade, Pure1 or Pure Fusion systems, especially production arrays with critical data - volumes, hosts, LUNs, snapshots, protection groups, pods, ActiveCluster, file systems, buckets, capacity, latency, replication, eradication, best practices, configuration audit.
---

# Managing Pure Storage in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **Reads:** Pure Fusion MCP server (read-only). Discover its tools at session start (Claude Code: ToolSearch "pure fusion"; OpenCode and others: the pure-fusion tools in your tool list). Cite array and timestamp for every value. If MCP is missing or fails, say so and give the user read-only CLI/REST commands. Never guess state.
- **Writes:** the change plan's command block, run by a human. Later write tools still go through the gate.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | list, monitor, alerts, health check | none |
| T1 additive | snapshot, create vol/host/FS, connect, add replication target | plan + "approve" |
| T2 modify | grow, rename, QoS, pgroup schedule/retention, export rules, host initiators/personality, enable replication, recover destroyed object | full plan + "approve" per T2 item |
| T3 destructive/disruptive | destroy, eradicate, disconnect, truncate, overwrite from snap, pod unstretch/promote/demote, replication teardown, SafeMode, upgrades, failover | full plan + user types object name; safety snapshot first; eradicate never in the same approval as destroy |

Mixed request → split by tier; each T2/T3 item gets its own approval.

## Facts not to get wrong
- `destroy` frees no space; it is recoverable during the eradication period (24h default, SafeMode can extend). `eradicate` is permanent, and space returns gradually.
- `truncate` cuts everything past the new size. Thin volumes: shrinking changes provisioned, not physical, capacity. Host shrinks first.
- Retention cuts prune existing snapshots on the next cycle.
- Connected or I/O-active means in use. Zero I/O for a few seconds is not proof of disuse.
- Stretched pod: changes affect both arrays. No change unless both are `online`.
- Enabling replication starts a full baseline transfer. Size it and schedule it.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said go ahead / I approve" | Approval before the plan existed approves nothing. Show the plan. |
| "It's additive / reversible, I'll just do it" | T1 still needs the plan. Reversibility is part of the plan. |
| "Emergency, I'll file the change after" | Use the terse emergency plan; approval still comes first. |
| "Nobody uses it" | Verify connections, I/O history, pgroups, clones. |
| "Destroy is reversible, so it's safe" | It doesn't free space and it breaks hosts now. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/best-practices.md: recommended configuration, read-only audit checks and fix tiers (use for best-practice or config reviews)
- references/flasharray.md: objects, commands by tier, pre-checks, ActiveCluster, capacity relief
- references/flashblade.md: FS, exports, S3, replica links
- references/fusion-and-pure1.md: MCP setup, tokens, Fusion, Pure1 API
- references/health-checks.md: health report format and thresholds
- references/incident-triage.md: lost LUN, latency, array full, replication, failover
