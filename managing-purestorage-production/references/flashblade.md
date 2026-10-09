# FlashBlade reference (Purity//FB 4.x)

Confirm CLI syntax with `--help` on the target blade. REST 2.x is the stable contract.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| File system | NFS/SMB namespace with a provisioned size (quota) | A hard limit below used space gives clients ENOSPC |
| Export / access policy | NFS rules (client, rw/ro, root-squash), SMB share policy | A changed rule cuts off clients instantly, mid-write |
| Object store account / user / key | S3 tenancy and credentials | Deleting a key breaks the apps using it |
| Bucket | S3 bucket, optional versioning and object lock | Object lock (compliance) cannot be undone |
| Snapshot / snapshot policy | FS snapshots on a schedule | Shortening a policy prunes old snapshots |
| Replica link | FS or bucket replication to another FB or to S3 | Breaking the link stops RPO protection |
| SafeMode | Locked snapshots, delayed eradication | Changes go through Pure Support |

## Read-only (T0)

CLI: `purearray list --space`, `purefs list`, `purefs list --space`, `purefs list --snapshot`, `purepolicy list`, `pureobjaccount list`, `pureobjbucket list`, `purealert list`, `purearray monitor`, `pureblade list`, `purehw list`.

REST 2.x GET: `/arrays`, `/arrays/space`, `/arrays/performance`, `/file-systems`, `/file-system-snapshots`, `/policies`, `/nfs-export-policies`, `/smb-share-policies`, `/object-store-accounts`, `/buckets`, `/file-system-replica-links`, `/bucket-replica-links`, `/alerts`, `/blades`, `/hardware`, `/clients/performance` (top NFS clients).

## Change operations by tier

| Tier | Operation | Notes / rollback |
|---|---|---|
| T1 | FS snapshot | Destroy the snapshot to roll back |
| T1 | Create FS, bucket, account, access key | Delete it (empty) to roll back |
| T2 | Resize FS | Growing is safe. Shrinking is allowed only above used space. Check hard-limit and default quotas. |
| T2 | Export / NFS rules / SMB policy | Record the old rule exactly. Test from one client before the rest. |
| T2 | Snapshot policy retention | Pruned snapshots can't be recovered |
| T2 | Bucket versioning / lifecycle rules | A lifecycle rule can expire data in bulk |
| T3 | Destroy FS / bucket | Recoverable during the eradication period. Check the period on the array before relying on it. |
| T3 | Eradicate | **Irreversible** |
| T3 | Disable protocol (NFS/SMB/S3) on an FS | Instant outage for every client |
| T3 | Delete access key / account | Apps fail on their next request |
| T3 | Break or delete replica link | DR copy stops updating. Re-seeding can take days. |
| T3 | Enable object lock (compliance mode) | Can't be disabled. Data can't be deleted until retention expires. |
| T3 | Promote / demote DR file system | Failover. Follow the DR runbook only. |

## Pre-checks
- Active clients: `/clients/performance` or `purearray monitor --client`. Any client means the object is in use.
- Used space vs. provisioned, and any quotas.
- Replica link status and lag before touching a replicated FS or bucket.
- Snapshot policies attached to the FS.
