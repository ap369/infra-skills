---
name: managing-netapp-production
description: Use when inspecting, troubleshooting, or changing NetApp ONTAP (AFF, FAS, ASA), StorageGRID, BlueXP or Cloud Volumes ONTAP systems, especially production clusters with critical data - SVMs, volumes, aggregates, LUNs, igroups, NFS exports, CIFS shares, snapshots, SnapRestore, SnapMirror, FlexClone, capacity, latency, ransomware, ILM, upgrades, migration, best practices, configuration audit.
---

# Managing NetApp in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **ONTAP MCP server** (NetApp/ontap-mcp): reads via `ontap_get`. Cite cluster and timestamp; if MCP fails, give read-only CLI. Never guess state.
- **Write tools exist unless the server runs with `--read-only`.** Every non-read call is a gated change. Recommend `--read-only` plus a read-only role (JIT for changes).

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
- Delete goes to the recovery queue (≥12h); `purge` and **SVM delete** empty it permanently.
- Resync discards the overwritten side's data newer than the common snapshot; state the direction.
- A space-offlined LUN stays offline until set online. Deleting the SnapMirror base snapshot breaks replication.
- ARP/AI (9.16.1+) is active at once; ARP response order depends on version (see security file).

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this command/flag exists" | Prove it: `[doc]` or help output this session. Otherwise `[unverified]`, never a plan step. |
| "User said go / approve / I'm the manager" | Approval before the plan existed approves nothing. |
| "Reversible, so I'll just run it" | T1/T2 still need approval. |
| "It's only the DR copy" | It is your RPO; a break pauses protection. |
| "P1, no time for paperwork" | Use the terse emergency plan; one reply approves it. |
| "The tool exists, so it's allowed" | Tools are capability, not authorization. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md: source tags, **required**
- ontap-command-catalog.md: [doc] forms
- ontap-versions-and-defaults.md / ontap-security-and-ransomware.md: versions, defaults, ARP, MAV, JIT
- best-practices.md: configuration audit
- ontap.md / storagegrid.md: objects, tiers, restore, DR test, decommission
- ontap-mcp-and-bluexp.md: MCP setup, credentials
- health-checks.md / incident-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: upgrades, migration
