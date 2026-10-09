# ECS / ObjectScale reference (ECS 3.6–3.8, ObjectScale 4.x on ECS hardware)

APIs:
- **Management REST API** on `https://<node>:4443`. Get a token from `GET /login` (basic auth), which returns the `X-SDS-AUTH-TOKEN` header, and release it with `GET /logout`.
- **S3 data API** on `https://<lb>:9021` (HTTP 9020).

Syntax and paths drift between releases. Confirm them against the API reference for the installed version. ObjectScale on Kubernetes (the software-defined edition) has a different management model. This file covers the ECS appliance lineage.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| VDC / site | One ECS cluster (rack of nodes) | Removing a VDC from a federation is a Dell-led procedure |
| Storage pool (varray) | Nodes and disks inside a VDC | Node and disk removal is Dell-led |
| Replication group (RG / vpool) | Which VDCs hold copies of the data | **Fixed at bucket creation.** Removing a VDC from an RG triggers massive re-replication or data loss. |
| Namespace | Tenant: users, buckets, quota, retention classes, compliance flag | Compliance namespaces can't be undone. Deleting one requires it to be empty. |
| Bucket | S3/Swift/NFS/CAS container: versioning, Object Lock, ADO, quota, lifecycle, policy | Owner, RG and file-system enablement are fixed at creation |
| Object user | S3 identity with up to **2 secret keys** at the same time | Deleting a key breaks every app using it |
| Management user | System Admin / **System Monitor** (read-only) / Namespace Admin / Security Admin | Use System Monitor for reads |
| ADO (access during outage) | Lets a bucket be read or written while a site is down | Can serve stale data. Toggling it is a decision about consistency semantics. |
| Retention / Object Lock / CAS retention | Immutability | COMPLIANCE mode and compliance namespaces can't be shortened or removed |

## Read-only (T0)

Management API (System Monitor token):
```
GET /dashboard/zones/localzone                       # health, capacity summary
GET /dashboard/zones/localzone/nodes                 # node status
GET /dashboard/zones/localzone/replicationgroups     # RG status, RPO / geo lag (field names vary by version)
GET /vdc/alerts?...                                  # alerts (filter by severity, acknowledged)
GET /object/capacity                                 # total / free
GET /vdc/data-services/varrays ; GET /vdc/data-service/vpools
GET /object/namespaces ; GET /object/namespaces/namespace/{ns}
GET /object/bucket?namespace={ns}                    # buckets
GET /object/bucket/{b}/info?namespace={ns}           # owner, RG, versioning, retention, ADO, quota, file-system
GET /object/bucket/{b}/quota?namespace={ns} ; /retention ; /lock
GET /object/billing/buckets/{ns}/{b}/info            # size, object count
GET /object/users?namespace={ns} ; GET /object/user-secret-keys/{uid}   # key metadata. Do not print the secrets.
GET /vdc/users ; GET /object/bucket/{b}/policy?namespace={ns}
```

S3 (read-only identity, **configuration only**):
```
aws --endpoint-url $EP s3api get-bucket-versioning --bucket B
aws --endpoint-url $EP s3api get-object-lock-configuration --bucket B
aws --endpoint-url $EP s3api get-bucket-lifecycle-configuration --bucket B
aws --endpoint-url $EP s3api get-bucket-policy --bucket B
aws --endpoint-url $EP s3api list-objects-v2 --bucket B --max-items 20 --query 'Contents[].{K:Key,S:Size,T:LastModified}'   # sample only
```
Never download object contents (`get-object`, `s3 cp` from a bucket) to "check" data. Tenant data isn't operator data.
Never run `aws s3 ls --recursive` or full listings on large buckets to get a size. Use the billing API (`/object/billing/...`), which is instant and costs nothing on the cluster.

## Change operations by tier

| Tier | Operation | Notes / rollback |
|---|---|---|
| T1 | Create namespace / bucket / object user / management user | Delete it (empty) to roll back. **The RG must be chosen right**: it can't be changed later. |
| T1 | Add a **second** secret key to a user (rotation start) | Expire or delete the new key |
| T2 | Quota (soft/hard), bucket ACL / policy, CORS, versioning enable | Record the old values. A hard quota below usage blocks writes. A policy can grant public or cross-tenant access, so review it as a security change. |
| T2 | Expire the old secret key after the apps rotate | Can't be un-expired, so treat it as T3 if apps aren't confirmed |
| T2 | ADO on/off | Consistency vs. availability. Needs the owner's sign-off. |
| T3 | Delete secret key / user | Apps fail immediately |
| T3 | **Lifecycle rule with Expiration / NoncurrentVersionExpiration / AbortIncomplete** | Mass deletion runs asynchronously and can't be undone. Scope it with a prefix or tag, check versioning, and do a dry-run count first. |
| T3 | Empty bucket (`s3 rm --recursive`, ECS "empty bucket" delete option) / delete bucket / delete namespace | **NONE** |
| T3 | Versioning suspend | Future overwrites destroy the previous version |
| T3 | **Object Lock / retention COMPLIANCE, compliance namespace, CAS retention increase** | Can't be shortened. The capacity is committed for the whole retention period. |
| T3 | Remove a VDC from an RG, PSO (permanent site outage), node/disk removal, upgrades | Dell support only |

## Pre-checks every change needs
1. Exact identity: namespace, bucket, user, RG. Get bucket info and billing (size, object count).
2. **Who uses it:** recent access (ECS bucket metering / access logs if enabled, load balancer logs), the object users with keys on the bucket, CAS/NFS/HDFS enablement.
3. **Protection:** versioning, Object Lock / retention, legal holds, geo replication status (RPO). Is this bucket another system's replication or backup target?
4. Capacity: storage pool used and garbage collection. **Deleting data doesn't free space immediately.** Garbage collection reclaims chunks over hours or days, and geo-replicated data is reclaimed at every site.
5. Health: alerts, nodes and disks, replication group status. No change during a site outage or rebalancing except the fix itself.

## Bucket decommission: the safe pattern
1. **Read:** bucket info, billing, retention, Object Lock and legal holds, compliance namespace, the newest object timestamps (is anything still writing?), and the owner and data-owner tags.
2. **T2 cool-off (reversible):** a bucket policy that denies `s3:*` to all principals except an admin role, for an agreed period (default 7 days). Save the previous policy for rollback. Anything that breaks shows itself.
3. **T3 (separate approval, the bucket name typed, written sign-off from the data owner or compliance):** empty the bucket server-side, using the ECS empty-bucket option of the delete API or a lifecycle rule that also expires noncurrent versions and incomplete uploads. Then delete the bucket. Check the exact API for the installed version first.
4. Space returns through garbage collection over days, at every site. Say so up front: deletion is not a same-day capacity fix.

## Lifecycle rules
- `put-bucket-lifecycle-configuration` **replaces every existing rule**. Back up the current config, merge it into the new one, and put the merged file in the plan.
- Expiration counts from **creation time**, not last access, so reference and metadata objects (Hive/Iceberg) that are old but still in use get deleted.
- On versioned buckets, `Expiration` only adds delete markers. Space comes back only with `NoncurrentVersionExpiration`.
- Scope rules by prefix or tag, and give the user a dry-run estimate (bounded listing per prefix) of what will expire.

## Object Lock / retention
- COMPLIANCE can't be undone by anyone, Dell included. Offer GOVERNANCE if it meets the requirement.
- A default retention applies only to objects written **after** it is set. Existing objects need per-object retention, a separate irreversible bulk job.
- Requires versioning. Check that ADO and file-system (NFS) access are compatible with it. Validate the exact configuration on a throwaway test bucket with a 1-day retention first.
- State the capacity commitment: everything written is kept for the full period.

## Leaked secret key: the safe pattern (emergency path, T1 + T3)
1. **Read:** list the user's keys (metadata only), the buckets they own, and recent access.
2. **T1 (emergency plan, one-word approval):** add a second key to the user, with the old key set to expire in **N minutes** if the version supports expiry. Otherwise keep both keys active briefly. The new secret goes **directly to a secrets manager or the requester through the secure channel**, never into chat or ticket text. Claude doesn't echo it.
3. The app team deploys the new key.
4. **T3 (typed user name):** delete the leaked key. If the app can't rotate in time, deleting the leaked key immediately is the user's call. Spell out the outage, then do it when they confirm.
5. **Post-checks:** only the new key is active. Watch for access denied errors from the old key (that's the attacker or a missed app).

Also tell the user to rotate wherever else the leaked secret was reused, and to purge it from git history.
