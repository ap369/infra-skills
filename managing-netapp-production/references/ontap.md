# ONTAP reference (AFF / FAS / ASA, ONTAP 9.x)

> **Command verification status:** ONTAP CLI forms in this skill were cross-checked against NetApp's *ONTAP 9 documentation* (2026-10-08, ONTAP 9.19.1). Commands listed in ontap-command-catalog.md, and ones that match it, are `[doc]`. Any other form, or a new parameter, is `[unverified]`. Confirm parameters on the target with `<command> ?` before use. See command-verification.md.


Syntax drifts between ONTAP releases. Confirm with `<command> ?` or the REST docs (`https://<cluster>/docs/api`) before putting a command in a change plan. Commands marked *(adv)* need `set -privilege advanced`, and that privilege change belongs inside the change plan.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Cluster / node / HA pair | Physical controllers; HA partner takes over on failure | Takeover and giveback disrupt LIFs that are not on their home port |
| Aggregate (local tier) | RAID groups of disks; volumes live on it | Over ~90% full, write performance and snapshot growth suffer |
| SVM (vserver) | Tenant: owns volumes, LIFs, protocols | Deleting an SVM takes everything in it |
| FlexVol / FlexGroup | Volume; NAS junction path or LUN container | `offline` or `unmount` means an instant client outage |
| LUN + igroup / NVMe namespace + subsystem | Block device mapped to initiators | Unmap, or removing an initiator, means an instant loss of the disk |
| Qtree | Sub-directory with quota/export policy | Quota changes can cause ENOSPC |
| Export policy + rules | NFS access by client match | Applied live; check with `vserver export-policy check-access` |
| CIFS share / ACL | SMB access | Applied live |
| LIF | IP/FC endpoint with home port | Modifying, migrating or deleting it drops sessions |
| Snapshot / snapshot policy | Point-in-time copy; policy-driven retention | A **volume** snapshot restore reverts the whole volume |
| SnapMirror / SnapVault | Async/sync replication (DR / backup) | Break makes the destination writable. Resync can discard data. |
| SnapLock / tamperproof snapshots / ARP | Immutability and anti-ransomware | Can't be undone, or weakens protection if disabled |
| MetroCluster / SM active sync | Synchronous sites | Switchover only through the DR runbook |
| Volume recovery queue | Deleted volumes are kept for at least 12h by default *(adv)* | `purge` is irreversible. **Deleting the SVM empties the queue** (docs p718). |

## Read-only commands (T0)

```
cluster show ; system health status show ; system health alert show
event log show -severity <=ERROR -time >1h
storage failover show                       # HA state, takeover possible
storage aggregate show -fields percent-used,availsize,state
storage aggregate show-space
volume show -vserver <svm> -fields size,used,percent-used,available,state,junction-path,autosize-mode,snapshot-policy,type
volume show-space -vserver <svm> -volume <vol>
volume snapshot show -vserver <svm> -volume <vol> -fields create-time,size,snapmirror-label
lun show -vserver <svm> -fields path,size,size-used,state,mapped,space-reserve
lun mapping show ; igroup show -fields initiator,protocol,ostype
vserver nvme subsystem map show ; vserver nvme namespace show
vserver export-policy rule show -vserver <svm> -policyname <p>
vserver export-policy check-access -vserver <svm> -volume <vol> -client-ip <ip> -authentication-method sys -protocol nfs3 -access-type read-write
vserver cifs share show ; vserver cifs session show
nfs connected-clients show -vserver <svm> -volume <vol>   # only clients with traffic in the last 48h; idle mounts invisible
network interface show -is-home false       # LIFs not on home port
snapmirror show -fields source-path,destination-path,state,status,lag-time,healthy,policy,schedule
snapmirror list-destinations
qos statistics workload latency show ; qos statistics performance show ; statistics show-periodic
security anti-ransomware volume show
volume recovery-queue show                  # (adv)
security audit log show -timestamp >1h      # who changed what (9.11+; older: event log / audit log files)
```

REST (via MCP `ontap_get`): `/api/cluster`, `/api/cluster/nodes`, `/api/storage/aggregates`, `/api/storage/volumes?fields=space,state,nas.path,autosize`, `/api/storage/snapshots` (per volume: `/api/storage/volumes/{uuid}/snapshots`), `/api/storage/luns`, `/api/protocols/san/igroups`, `/api/protocols/san/lun-maps`, `/api/protocols/nfs/export-policies`, `/api/protocols/nfs/connected-clients`, `/api/protocols/cifs/shares`, `/api/network/ip/interfaces`, `/api/snapmirror/relationships?fields=state,lag_time,healthy`, `/api/support/ems/events`, `/api/security/audit/messages`, `/api/storage/qos/policies`.

## Change operations by tier

| Tier | Operation | CLI / MCP tool | Rollback |
|---|---|---|---|
| T1 | Snapshot | `volume snapshot create -vserver S -volume V -snapshot CHG1234` / `create_snapshot` | delete the snapshot |
| T1 | Create vol / LUN / qtree / share | `volume create`, `lun create`, ... / `create_*` | delete (empty) |
| T1 | FlexClone for testing or recovery | `volume clone create -parent-volume V -parent-snapshot S -flexclone V_clone` | delete the clone |
| T1 | Map LUN / add initiator | `lun map`, `igroup add` / `create_lun_map`, `add_igroup_initiator` | unmap or remove. **Check the LUN id isn't in use by that host.** |
| T1 | SnapMirror update (manual transfer) | `snapmirror update` | n/a |
| T2 | Grow volume / autosize | `volume size -new-size +500g`, `volume modify -autosize-mode grow -max-autosize` / `modify_volume` | shrink back only if the space is unused |
| T2 | Grow LUN | `lun resize -size +100g` (then the host rescans) | can't shrink safely |
| T2 | Export rule / CIFS ACL / QoS / snapshot policy / schedule | `vserver export-policy rule modify`, ... / `modify_*` | record the old values verbatim first |
| T2 | Snapshot policy retention cut | `volume snapshot policy modify-schedule -count` | snapshots pruned meanwhile are gone |
| T2 | SnapMirror quiesce / resume | `snapmirror quiesce` / `resume` | inverse |
| T2 | Recover deleted volume | `volume recovery-queue recover -vserver S -volume V_<id>` *(adv)* | n/a |
| T2 | Single-file / folder restore | `volume snapshot restore-file -path ... [-restore-path ...]`, or copy from `.snapshot/` / `~snapshot` | restore to an alternate path first |
| T3 | Volume offline / unmount | `volume offline`, `volume unmount` / `modify_volume` | online / mount. **The outage happens in between.** |
| T3 | Delete volume | `volume offline` then `volume delete` / `modify_volume` (delete) | recovery queue, 12h default *(adv)* |
| T3 | Purge recovery queue | `volume recovery-queue purge` *(adv)* | **NONE** |
| T3 | Delete snapshot | `volume snapshot delete` / `modify_snapshot` | **NONE** |
| T3 | **Volume snapshot restore (SnapRestore)** | `volume snapshot restore -snapshot S` / `restore_snapshot` | **NONE.** Discards all data written after S *and every newer snapshot*. Can break SnapMirror. |
| T3 | Unmap LUN / remove initiator / delete igroup | `lun mapping delete`, `igroup remove` / `delete_lun_map`, `remove_igroup_initiator` | remap with the **same LUN id** |
| T3 | Shrink volume or LUN | `volume size -new-size <smaller>`, `lun resize -size <smaller>` | none for LUNs (truncates data) |
| T3 | SnapMirror break | `snapmirror break` / `modify_snapmirror` | resync, which discards destination changes |
| T3 | SnapMirror resync / reverse resync | `snapmirror resync` | **NONE:** data on the target side newer than the common snapshot is lost |
| T3 | SnapMirror delete / release | `snapmirror delete`, `snapmirror release` | re-baseline (full transfer) |
| T3 | LIF modify / migrate / delete | `network interface modify/migrate/delete` | revert. Sessions drop. |
| T3 | SVM / protocol service delete or disable | `vserver delete`, `vserver nfs delete` / `vserver nfs modify` (disabling access), `delete_*_service` | rebuild. Total outage for the SVM. |
| T3 | Cluster/SVM peer delete | `delete_cluster_peer`, `delete_svm_peer` | re-peer. Breaks every SnapMirror over it. |
| T3 | ARP disable, SnapLock, tamperproof snapshot settings | `security anti-ransomware volume disable`, ... | weakens ransomware protection, or is irreversible |
| T3 | Takeover / giveback / reboot / upgrade (ANDU) / MetroCluster switchover | `storage failover takeover`, `system node reboot`, `cluster image update` | NetApp Support or DR runbook only |

## Pre-check queries every change needs
1. The object exists. Get its exact SVM, volume and LUN identity (UUID from REST) so the right object is changed.
2. **Who uses it:** NFS connected clients (only the last 48h of traffic), CIFS sessions, LUN mapping and igroup initiators, QoS/latency stats showing live I/O. Zero I/O for a few seconds is not proof of disuse. Backup and month-end jobs sit idle most of the time.
3. Protection: snapshot policy, existing snapshots, SnapMirror relationships *both directions* (`snapmirror show` and `snapmirror list-destinations`), SnapVault, ARP and SnapLock state.
4. Capacity: volume and aggregate free space, snapshot reserve, autosize settings, fractional reserve.
5. Dependencies: FlexClones (`volume clone show`). A parent volume or snapshot that a clone depends on can't be deleted. Also check junction children, since unmounting the parent hides them.
6. HA and cluster health: `storage failover show`, LIFs on their home ports, no ongoing takeover.

## Full volume / LUN offline: relief ranked by safety
A space-reserved or thin LUN goes **offline** when its volume runs out of space, to protect the data.
1. **Grow the volume** (T2) if the aggregate has room. This is the fastest safe fix. Then bring the LUN online with `lun modify -vserver S -path P -state online` (T2).
2. **Enable autosize** (`-autosize-mode grow`, set a max) to prevent a repeat.
3. Snapshot space: identify the snapshots that hold the most space (`volume snapshot compute-reclaimable`, *adv*). Deleting a snapshot is **T3 and permanent**. Before deleting, check it isn't a SnapMirror or SnapVault base snapshot (deleting the base breaks replication) or the only restore point.
4. Move the volume (`volume move start`) to a less-full aggregate: online, but heavy I/O.

Never delete snapshots in bulk "to make room" without the list and an approval.

## Restoring deleted files: choose the narrowest restore
1. **Self-service:** clients copy from `.snapshot` (NFS) or Previous Versions / `~snapshot` (SMB). Read-only, so zero risk.
2. **Single-file/folder SnapRestore:** `volume snapshot restore-file`, preferably to an alternate `-restore-path` first.
3. **FlexClone** from the snapshot, then copy the data back. Use this when there is a lot of data.
4. **Whole-volume SnapRestore:** last resort. Everything written since the snapshot is lost, every newer snapshot is deleted, and SnapMirror may need a re-baseline. It needs the full T3 gate and owner sign-off.

## SnapMirror DR test: the safe pattern
- Prefer a **FlexClone of the destination volume** (from the latest SnapMirror snapshot). The app team tests on the clone, replication keeps running, and you delete the clone afterwards. No break, no resync.
- If a real break is required:
  1. `snapmirror update`, then `quiesce`
  2. `break` (destination becomes RW)
  3. test
  4. `snapmirror resync` **from the original source to the destination**. This discards the test writes on the destination, which is intended.
- Never run `resync` in the reverse direction (destination → source) unless it is a real failback. It overwrites production.
- Record the policy, schedule and relationship type before you start.

## Decommission pattern (volume / LUN / share)
1. **Read:**
   - who uses it: NFS connected clients, CIFS sessions, LUN maps, igroup initiators, I/O history (Harvest/AIQUM over days)
   - SnapMirror in **both** directions, SnapVault
   - FlexClone children, junction children
   - snapshot policy
2. **Step 0:** a final snapshot named `decom-<ticket>`. If backup or retention requires it, keep the SnapMirror/SnapVault copy at the destination for the agreed retention.
3. **Stage 1 (T3, reversible):** remove access. Unmap LUNs (record the LUN IDs) or remove the share / unmount the junction. Then `volume offline`. The data stays intact, and online/remap reverses it.
4. **Quarantine:** default 7 days.
5. **Stage 2 (T3, separate approval, volume name typed):**
   1. release or delete SnapMirror relationships deliberately (state the direction)
   2. `volume delete`, which goes into the recovery queue (12h default)
6. **Recovery queue:** let it expire on its own. `purge` is only for a capacity emergency, as its own approval.

## SnapMirror operational facts (ONTAP docs)
- `snapmirror quiesce`, `break` and `resync` are run **from the destination SVM or cluster** (p236, p2689).
- `-quick-resync true` shortens a resync but **can lose storage-efficiency savings**. Since 9.13.1 ONTAP tries it by default when the volume has no clones and uses MirrorAllSnapshots (p2706).
- A resync replicates only snapshots newer than the **last common snapshot** (p2645). Deleting that snapshot forces a re-baseline.
- SnapMirror synchronous auto-resync starts only after transfer failures (takeover, network). It never starts after a user's quiesce or break. **StrictSync out of sync stops primary I/O** (p2644).
- FlexGroup break and resync briefly block client access to the destination. If an operation fails, retry it, because some constituents can stay blocked (p906).
- After restoring a replicated volume from a snapshot, update the mirrors manually (p2316).
