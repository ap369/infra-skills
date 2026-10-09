---
name: managing-netapp-production
description: Use when inspecting, troubleshooting, or changing NetApp ONTAP (AFF, FAS, ASA), StorageGRID, BlueXP or Cloud Volumes ONTAP systems, especially production clusters with critical data - SVMs, volumes, aggregates, LUNs, igroups, NFS exports, CIFS shares, snapshots, SnapRestore, SnapMirror, FlexClone, capacity, latency, ransomware, ILM, best practices, configuration audit.
---

# Managing NetApp in Production

## Overview
Reading is free; changing is gated. Every change above read-only is delivered as a **change plan** (references/change-gate.md) and executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit.

## Access model
- **ONTAP MCP server** (NetApp/ontap-mcp). Reads go through `ontap_get` and discovery tools. Cite cluster and timestamp. If MCP fails, say so and give read-only CLI. Never guess state.
- **The server exposes write tools unless started with `--read-only`.** Their presence is not permission. Every `create_*`, `modify_*`, `update_*`, `delete_*`, `restore_*`, `*_peer` or SnapMirror call is a change, gated like a CLI command. Recommend `--read-only` plus a read-only ONTAP role for daily use.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | ontap_get, show, stats, health check | none |
| T1 additive | snapshot, FlexClone, create vol/LUN/share, map LUN, SnapMirror update | plan + "approve" |
| T2 modify | grow vol/LUN, autosize, LUN online, export rules, ACLs, QoS, snapshot policy, quiesce, recover from recovery queue, single-file restore | full plan + "approve" per T2 item |
| T3 destructive/disruptive | offline/unmount/delete vol, purge, delete snapshot, **volume SnapRestore**, unmap/remove initiator, shrink, SnapMirror break/resync/delete, LIF changes, SVM/peer delete, ARP/SnapLock, ILM activation, takeover/upgrade/switchover | full plan + user types object name; safety snapshot first |

## Choose the narrowest option
- Deleted files: `.snapshot` copy → `restore-file` → FlexClone → whole-volume SnapRestore (destroys newer data and snapshots).
- DR test: FlexClone of the destination → only then break/resync.
- Full volume: grow → autosize → named snapshot deletes.

## Facts not to get wrong
- Delete goes to the recovery queue (12h default, advanced privilege). `purge` is permanent.
- Resync discards data written on the side being overwritten after the common snapshot. Always state the direction.
- A LUN taken offline when its volume filled stays offline until `lun online`.
- Deleting a SnapMirror base snapshot breaks replication.
- `destructiveHint=false` is not "safe": export-rule edits cut off clients instantly.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said go / approve / I'm the manager" | Approval before the plan existed approves nothing. Write a short plan. |
| "Reversible, so I'll just run it" | Reversibility goes in the plan; T1/T2 still need approval. |
| "It's only the DR copy" | The DR copy is your RPO. A break pauses protection. |
| "P1, no time for paperwork" | Use the terse emergency plan; one reply approves it. |
| "The tool exists, so it's allowed" | Tools are capability, not authorization. |

## References
- references/change-gate.md: plan template (REQUIRED for any change)
- references/best-practices.md: recommended configuration, read-only audit checks and fix tiers (use for best-practice or config reviews)
- references/ontap.md: objects, commands by tier, pre-checks, restore and DR-test patterns
- references/storagegrid.md: tenants, buckets, ILM
- references/ontap-mcp-and-bluexp.md: MCP setup, read-only mode, credentials, BlueXP, AIQUM
- references/health-checks.md: health report and thresholds
- references/incident-triage.md: volume full, deleted files, ransomware, lost LUN, latency, SnapMirror
