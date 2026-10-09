# Incident triage playbooks

During an incident, diagnosis is T0 and goes fast. The fix still goes through the change gate, using its **emergency path**: same steps, terse write-up, one confirmation per step. Urgency changes the format, not the safety.

Order for every incident:
1. **Scope:** which hosts, apps, arrays, and since when.
2. **Read** the data.
3. **Hypothesis**, with evidence.
4. **Smallest reversible fix**, gated.
5. **Verify.**
6. **Timeline notes** for the postmortem.

## Host lost its LUN / datastore
1. `purehost list --connect <host>`: is the volume still connected? Is the LUN id unchanged?
2. `purevol list --pending`: was the volume destroyed? If so, `purevol recover` (T3 gate, emergency path). It's the classic fix.
3. `pureport list --initiator`: are the host's WWNs/IQNs logged in? If not, the problem is on the fabric or host side (zoning, HBA, iSCSI session). The array can't fix it. Hand over to the SAN/host team with the evidence.
4. `purehost list --all <host>`: were initiators removed, or the personality changed? Check the audit log: `pureaudit list` (recent changes, who, when).
5. ActiveCluster: `purepod list --array`. If the local array is offline for the pod, hosts should use the paths to the peer. Check the host multipathing *before* touching the pod.
6. ESXi side, for the user to run: rescan the HBAs, `esxcli storage core path list`, and check for an APD/PDL state.

Don't "reconnect everything" or re-create the host blindly. A wrong LUN id or duplicate initiator can corrupt VMFS/cluster resources on other hosts.

## Latency spike
1. `purearray monitor` and `/arrays/performance`. Is it array-wide or one volume?
2. `purevol monitor` and `/volumes/performance` sorted by latency or IOPS: find the top talkers.
3. Large block size with high bandwidth points at a backup or clone job. Mirrored writes in a pod point at link latency between the sites.
4. Check for QoS limits being hit (`purevol list --qos`), hardware alerts, and a running Purity upgrade or failover.
5. Remediations are T2: QoS on the noisy neighbour, rescheduling the job. Never reboot controllers.

## Array full (≥ 90%)
Follow "Capacity relief, ranked by safety" in flasharray.md.
- Report: what is consuming the space (volumes, snapshots, shared, destroyed-pending) and how fast it is growing.
- Propose T1 and T2 relief first. Eradication is a T3 action with a named owner, and it's never the first move.
- At 100% the array goes read-only for writes. Escalate to Pure Support early: they can advise on GC and SafeMode.

## Replication broken / lagging
1. `purearray list --connect` (status, throttle).
2. The last successful snapshot on the target.
3. Network/link checks, for the user to run.

Re-creating a connection or pgroup target is T3: target-side snapshots may be lost.

## Failover (ActiveCluster / ActiveDR / async DR)
Only via the site DR runbook and with the incident commander's approval. Claude prepares the checklist and reads the state. It never initiates promote, demote or unstretch on its own judgement.
