# VNX reference (VNX1 / VNX2, Block OE 5.32/5.33, File OE 7.x/8.x)

**VNX is end of life.** Upgrades, parts and support contracts may be limited, so check the support status before planning any NDU or hardware action. Syntax drifts between OE versions. Confirm with `naviseccli -help <cmd>` and `<nas_cmd> -help`.

## Object model

Block side (SP A / SP B, naviseccli):

| Object | Gotchas |
|---|---|
| RAID group / storage pool / LUN | Pool LUNs (thin/thick) vs. RAID group LUNs (FLARE) |
| SP ownership (default / current) | Trespass moves LUN ownership between SPs. Host multipath must handle it (ALUA failover mode 4, or PowerPath). |
| Storage group | Masking: hosts + LUNs with HLU ids. Removing a LUN or host means an instant loss. |
| MirrorView/S, MirrorView/A, SAN Copy | Replication. Fracture or promote are DR operations. |
| SnapView (snapshots/clones), VNX Snapshots | Rollback overwrites the source |
| FAST Cache / FAST VP | Disabling FAST Cache flushes it and hurts performance |

File side (Control Station, Data Movers, nas_* / server_* commands):

| Object | Gotchas |
|---|---|
| Data Mover (server_2, server_3...) + standby | Failover means a brief outage for clients |
| VDM, file system, checkpoint (SnapSure) | Checkpoint restore overwrites the file system |
| Exports (`server_export`), CIFS servers, interfaces | Changes are live |
| Replicator (`nas_replicate`) | Failover, switchover and reverse are DR operations |

## Read-only (T0)
Block:
```
naviseccli -h <SPA> getagent ; naviseccli -h <SPB> getagent        # revision, serial, both SPs
naviseccli -h <SPA> faults -list ; getcrus ; getlog -100
naviseccli -h <SPA> storagepool -list -prcntFull -availableCap -consumedCap
naviseccli -h <SPA> lun -list -default -owner -curowner           # pool LUN ownership (check flags with -help)
naviseccli -h <SPA> getlun -owner -default -trespass              # RAID-group LUNs
naviseccli -h <SPA> storagegroup -list -host                      # masking
naviseccli -h <SPA> port -list -hba                               # host initiators logged in
naviseccli -h <SPA> mirror -async -list ; mirror -sync -list
naviseccli -h <SPA> ndu -list                                      # installed packages
```
File (Control Station, as nasadmin; run with `-h` where supported):
```
nas_checkup ; nas_server -list -all ; server_sysstat ALL
nas_fs -list ; server_df ALL ; fs_ckpt <fs> -list
server_export ALL -list ; server_ifconfig ALL -all
nas_replicate -list ; nas_replicate -info -all
```

## Change operations by tier

| Tier | Operation | Notes / rollback |
|---|---|---|
| T1 | Snapshot / checkpoint, create LUN / FS | Delete it to roll back |
| T1 | `spcollect` | Diagnostic, adds SP load. Fine during an incident. Tell the user it was run. |
| T2 | Trespass LUNs back to their default owner (`trespass mine` sent to the owning SP, or `trespass lun <n>`) | Only after the SP has a confirmed healthy state and host paths are verified. Trespass again to roll back. |
| T2 | Expand LUN / FS, export option changes, FAST Cache enable | Record the old values |
| T3 | Remove LUN/host from a storage group, destroy LUN / FS | Host outage, or **NONE** (data gone) |
| T3 | Snapshot rollback / checkpoint restore | Overwrites newer data |
| T3 | MirrorView fracture/promote, Replicator failover/switchover/reverse | DR runbook only |
| T3 | Data Mover failover, SP reboot, NDU / OE upgrade | Dell support. NDU reboots each SP in turn, trespassing everything twice. |

## Decommission pattern (LUN / file system)
1. **Read:**
   - storage group membership (HLU IDs)
   - host logins, I/O history
   - MirrorView/Replicator, snapshots/checkpoints
2. **Step 0:** a final snapshot or checkpoint if capacity allows. Otherwise keep a verified backup.
3. **Stage 1 (T3, reversible):** remove the LUN from its storage group (record the HLU), or unexport/unmount the FS.
4. **Quarantine:** default 7 days.
5. **Stage 2 (T3, separate approval, name typed):** fracture/remove mirrors deliberately, then destroy the LUN/FS. **No recycle bin.**
