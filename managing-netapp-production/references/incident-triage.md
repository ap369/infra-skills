# Incident triage playbooks

During an incident, diagnosis is T0 and goes fast. The fix still goes through the change gate's **emergency path**: same steps, terse write-up, approval before execution. Urgency changes the format, not the safety.

Order for every incident:
1. **Scope:** which hosts, apps, clusters, and since when.
2. **Read** the data.
3. **Hypothesis**, with evidence.
4. **Smallest reversible fix**, gated.
5. **Verify.**
6. **Timeline notes.**

## Volume full / LUN offline
1. `volume show -fields percent-used,available,autosize-mode,max-autosize` and the aggregate's free space.
2. `lun show -fields state`: a LUN that went offline because of space stays offline until someone brings it back online.
3. Fix, in order of safety (see "Full volume / LUN offline" in ontap.md):
   1. Grow the volume (T2).
   2. `lun online` (T2).
   3. Enable autosize (T2).
   4. Delete snapshots only from an approved, explicit list (T3). Never delete SnapMirror/SnapVault base snapshots.
4. Verify that the host sees the disk again. The host or DBA checks the filesystem and database.

## Files or folders deleted / corrupted
Use the narrowest restore that works: self-service `.snapshot` → `restore-file` to an alternate path → FlexClone → whole-volume SnapRestore (last resort, T3, it destroys newer data). See ontap.md, "Restoring deleted files".

## Ransomware suspected (ARP alert, mass renames, encrypted extensions)
1. Don't delete any snapshot and don't restore yet. Snapshots are the recovery path.
2. Read: `security anti-ransomware volume attack-reports` / ARP events, affected volumes, and the snapshots ARP took.
3. Propose containment (T2/T3, gated): block the offending clients (export rule or CIFS session), take snapshots of affected volumes, and lock them (tamperproof) if available.
4. Restore from the last clean snapshot to a FlexClone, validate it, and switch over. Engage the security team and NetApp Support.

## Host lost its LUN / NFS mount
1. Mapping: `lun mapped show`, `igroup show`. Is the initiator still in the igroup? Is the LUN id unchanged?
2. Volume or LUN state: online? In the recovery queue?
3. LIFs: `network interface show`. Check they're up and on their home port, and look for a recent failover.
4. NFS: `vserver export-policy check-access` for the client IP.
5. Audit: `security audit log show`. Who changed what?
6. If the initiators aren't logged in, the problem is on the fabric or host side. Hand it over with the evidence.

## Latency spike
`qos statistics volume latency show` and Harvest show which volume and which layer: network, frontend, cluster interconnect, data, disk, or a QoS limit. Find the top talkers. Then check for a running takeover, a volume move, a SnapMirror baseline, or a deduplication/compaction scan. Remediation is T2 (QoS, rescheduling). Never reboot or fail over a node to "clear" latency.

## SnapMirror broken / lagging
`snapmirror show -fields healthy,unhealthy-reason,lag-time`, the cluster and SVM peer state, intercluster LIFs. Look at the last transfer error. Try a `snapmirror update` first (T1). Resync and re-baseline are T3.

## Failover (HA takeover, MetroCluster switchover, SnapMirror DR activation)
Only via the site DR runbook and with the incident commander's approval. Claude prepares the checklist and reads the state. It never initiates takeover, switchover or a DR break on its own judgement.
