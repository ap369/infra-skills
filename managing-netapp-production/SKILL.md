---
name: managing-netapp-production
description: Use when inspecting, troubleshooting, or changing NetApp ONTAP (AFF, FAS, ASA), StorageGRID, BlueXP or Cloud Volumes ONTAP systems, especially production clusters with critical data - SVMs, volumes, aggregates, LUNs, igroups, NFS exports, CIFS shares, snapshots, SnapRestore, SnapMirror, FlexClone, capacity, latency, ransomware, ILM, upgrades, migration, best practices, configuration audit.
---

# Managing NetApp in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice.

## Access model
- **ONTAP MCP server** (NetApp/ontap-mcp). Reads go through `ontap_get` and discovery tools. Cite cluster and timestamp. If MCP fails, give read-only CLI. Never guess state.
- **Write tools exist unless the server runs with `--read-only`.** They are capability, not permission. Every non-read tool call is a change, gated like a CLI command. Recommend `--read-only` plus a read-only ONTAP role.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | ontap_get, show, stats, health check, audit | none |
| T1 additive | snapshot, FlexClone, create vol/LUN/share, map LUN, SnapMirror update | plan + "approve" |
| T2 modify | grow vol/LUN, autosize, LUN online, export rules, ACLs, QoS, snapshot policy, quiesce, recovery-queue recover, file restore | plan + "approve" per item |
| T3 destructive/disruptive | offline/unmount/delete vol, purge, delete snapshot, **volume SnapRestore**, unmap, shrink, SnapMirror break/resync/delete, LIF changes, SVM/peer delete, ARP/SnapLock, ILM activation, takeover/upgrade/switchover | plan + typed object name; snapshot first |

## Narrowest option first
- Deleted files: `.snapshot` copy → `restore-file` → FlexClone → volume SnapRestore (destroys newer data).
- DR test: FlexClone of the destination before break/resync.
- Full volume: grow → autosize → named snapshot deletes.

## Key facts
- Delete goes to the recovery queue (12h default). `purge` is permanent.
- Resync discards data written after the common snapshot on the overwritten side. Always state the direction.
- A space-offlined LUN stays offline until `lun online`. Deleting a SnapMirror base snapshot breaks replication.
- `destructiveHint=false` isn't "safe": export-rule edits cut off clients instantly.

## Rationalizations
| Thought | Reality |
|---|---|
| "User said go / approve / I'm the manager" | Approval before the plan existed approves nothing. |
| "Reversible, so I'll just run it" | Reversibility goes in the plan; T1/T2 still need approval. |
| "It's only the DR copy" | The DR copy is your RPO. A break pauses protection. |
| "P1, no time for paperwork" | Use the terse emergency plan; one reply approves it. |
| "The tool exists, so it's allowed" | Tools are capability, not authorization. |

## References
- change-gate.md: plan template, **required for any change**
- best-practices.md: configuration audit
- ontap.md / storagegrid.md: objects, commands by tier, restore, DR test, decommission
- ontap-mcp-and-bluexp.md: MCP setup, read-only mode, credentials
- health-checks.md / incident-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: upgrades, tech refresh
