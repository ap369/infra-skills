# PowerMax / VMAX reference (Solutions Enabler symcli, Unisphere for PowerMax)

Covers PowerMax 2000/8000/2500/8500 (PowerMaxOS 5978/10), VMAX All Flash 250F–950F and VMAX3 100K–400K (HYPERMAX OS 5977), and VMAX classic 10K/20K/40K (Enginuity 5876: thin pools, FAST VP, TimeFinder Clone/VP Snap instead of SnapVX). Syntax drifts between SE versions. Confirm with `<cmd> -h` before putting a command in a change plan. Add `-sid <SID>` to every command. Never rely on a default SID.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Device (TDEV) | Thin volume, hex ID (e.g. `00A1F`) | Devices can belong to several SGs. Check them all before removing one. |
| Storage group (SG) | Device set: unit of masking, SL, SnapVX, SRDF | Parent/child (cascaded) SGs: changing a child affects the parent's view |
| Initiator group (IG) / port group (PG) | Host WWNs/IQNs and FA ports | Cascaded IGs. Removing a WWN means the host loses paths. |
| Masking view (MV) | SG + IG + PG = host access | Deleting it means an instant loss of every device for those hosts |
| SRP / service level | Capacity pool / performance target | SRP is shared array-wide. Capacity is a fleet decision. |
| SnapVX snapshot | Targetless snapshot of an SG | `secure` snaps can't be terminated until they expire. `restore` overwrites the source. |
| Linked target | Snapshot presented on target devices | `link -copy` / `relink` overwrite the target devices' data |
| SRDF (S / A / Metro) | Replication, R1 → R2 in an RDF group | Suspend pauses DR. Resync makes R2 inconsistent until it finishes. Failover/swap only per the DR runbook. |
| Device group / composite group / SG-based SRDF | Management handles for SRDF | Check what the handle actually contains before acting on it |

## Read-only commands (T0)

```
symcfg list ; symcfg -sid <SID> list -v                 # arrays, code level
symcfg -sid <SID> list -srp -detail                      # SRP capacity, subscription, DRR
symcfg -sid <SID> list -dir all -v                       # director / port status
symevent -sid <SID> list -start <time>                   # events / errors
symaudit -sid <SID> list -start <time> -v                # who changed what
symdisk -sid <SID> list -failed
symsg -sid <SID> list ; symsg -sid <SID> show <SG>       # SG members, child/parent, SL, MV
symdev -sid <SID> list -sg <SG> ; symdev -sid <SID> show <dev>   # SGs, SRDF, SnapVX, size, allocations
symaccess -sid <SID> list view ; symaccess -sid <SID> show view <MV> -detail
symaccess -sid <SID> list logins [-dirport 1D:4]         # are host WWNs logged in?
symsnapvx -sid <SID> -sg <SG> list -detail [-linked]
symrdf -sid <SID> list -rdfg <n> ; symcfg -sid <SID> list -rdfg all
symrdf -g <DG> query [-rdfa] ; symrdf -sid <SID> -sg <SG> -rdfg <n> query
symstat -sid <SID> -type REQUESTS -sg <SG> -i 10 -c 6    # live I/O
symaccess -sid <SID> backup -file <path>                 # local backup of masking config (writes a local file only)
```
Unisphere REST (`https://<unisphere>:8443/univmax/restapi/<ver>/...`): `sloprovisioning/symmetrix/<SID>/storagegroup`, `/volume`, `/maskingview`, `/host`, `/portgroup`, `replication/symmetrix/<SID>/storagegroup/<SG>/snapshot`, `replication/symmetrix/<SID>/rdf_group`, `system/symmetrix/<SID>/alert`. Python: PyU4V. Ansible: `dellemc.powermax`.

## Change operations by tier

| Tier | Operation | Command (sketch) | Rollback |
|---|---|---|---|
| T1 | SnapVX snapshot (non-secure, with TTL) | `symsnapvx -sid S -sg SG establish -name CHG123 -ttl -delta 7` | `terminate` |
| T1 | Create devices / SG / IG / PG / MV | `symdev create -tdev -cap N -captype gb -N k -sg SG`, `symsg create`, `symaccess create view` | delete (unused only) |
| T1 | Add device to an SG in a masking view | `symsg -sg SG add dev <dev>` | remove: T3 once the host uses it |
| T1 | Link a snapshot to **new, empty** target devices | `symsnapvx -sg SG -lnsg TGT_SG link -snapshot_name X` | unlink |
| T2 | Expand device | `symdev -sid S modify <dev> -cap N -captype gb -devs ...` (SRDF pairs: R2 first or both, per SE docs) | none (no shrink) |
| T2 | Service level / host I/O limit | `symsg -sg SG set -slo ...`, `symsg -sg SG set -bw_max/-iops_max` | previous values |
| T2 | SRDF resume / incremental establish | `symrdf -g DG resume` / `establish` | suspend (R2 inconsistent until synchronized) |
| T2 | SRDF suspend / split | `symrdf -g DG suspend` / `split` | resume. DR is paused meanwhile. |
| T2 | Add initiator / port to IG/PG | `symaccess -type initiator add -wwn` | remove: T3 |
| T3 | Delete masking view | `symaccess -sid S delete view -name MV` | recreate from the backup file. **The host outage happens in between.** |
| T3 | Remove device from SG in an MV / remove initiator / remove port | `symsg -sg SG remove dev`, `symaccess remove -wwn` | re-add, same LUN address |
| T3 | Deallocate / delete devices | `symdev -sid S free -all -devs <list>`, `symconfigure ... delete dev` | **NONE.** Data is gone. |
| T3 | SnapVX restore | `symsnapvx -sg SG restore -snapshot_name X` | **NONE** for data written after the snapshot. Take a fresh snapshot first. |
| T3 | Link `-copy` / relink onto devices that hold data | `symsnapvx link -copy`, `relink` | **NONE** for the target's previous data |
| T3 | Terminate snapshot | `symsnapvx terminate` | **NONE** |
| T3 | Secure snapshot | `establish -secure` | can't be terminated early: capacity is locked until expiry |
| T3 | SRDF `establish -full`, `failover`, `failback`, `swap`, `deletepair`, `createpair -establish` on devices with data | `symrdf ...` | DR runbook only. Data on the overwritten side is lost. |
| T3 | Port/director disable, code upgrade, SRP/drive changes | Dell support | n/a |

## Pre-checks every change needs
1. Exact identities: SID, SG, device hex IDs (from `symsg show`). Never act on a pattern.
2. **Who uses it:** the MVs containing the SG, including through parent SGs (`symaccess list view -detail`), IG logins (`list logins`), and live I/O (`symstat`). Zero I/O for a minute isn't proof of disuse. Batch, backup and month-end jobs exist.
3. Other memberships: is each device in other SGs? `symdev show` lists them.
4. Replication: SRDF state on both sides, SnapVX snapshots and **linked targets** (a device can be someone else's link target).
5. Capacity: SRP used and subscription, and the impact of snapshot deltas.
6. Health: `symevent`, failed disks, director status. No change on a degraded array except the fix itself.

## Decommission pattern (MV → devices)
1. Back up the masking config (`symaccess backup`). Take a SnapVX snapshot of the SG with a TTL covering the quarantine period.
2. **Stage 1 (T3):** delete the MV, or remove the IG. Hosts lose access, the data stays intact, and recreating the MV fully reverses it.
3. **Quarantine:** wait an agreed period (default 7 days) for anything that breaks.
4. **Stage 2 (T3, separate approval with the device list typed):** terminate the snapshots, empty and delete the SG, `free -all`, delete the devices.

Never combine stage 1 and stage 2 in one approval.

## SRDF/A suspended after a link outage
- R2 holds the last **consistent** image. That's your DR copy right now.
- `symrdf -g DG query`: check invalid tracks on R1/R2. Is any R2 device RW (written at DR)?
- Before resyncing: **gold copy.** Take a SnapVX snapshot of the R2 SG on the DR array (T1). During resync R2 is inconsistent, and the gold copy is the only restartable image.
- Use `resume` or an incremental `establish`. Use `-full` only if the track tables are invalid, and that needs a T3 plan explaining why.
- Afterwards, enable consistency (`symrdf -g DG enable`) and confirm with `verify -consistent`.
