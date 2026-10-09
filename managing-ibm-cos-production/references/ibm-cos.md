# IBM Cloud Object Storage (Cleversafe dsNet, ClevOS 3.x) reference

Components:
- **Manager:** management UI and REST API.
- **Accessers:** S3 endpoints, grouped in access pools.
- **Slicestors:** store erasure-coded slices, grouped in device sets that form storage pools.

The Manager REST API lives at `https://<manager>/manager/api/json/1.0/<operation>.adm` with HTTP basic auth. Operation names and parameters vary by ClevOS release, so use the Manager REST API / Developer Guide for the installed version. S3 is served on the Accessers (or a load balancer in front of them). This file covers on-prem dsNet, not the IBM Cloud public service.

## Information Dispersal (IDA): the core safety math
Each vault has an IDA of **width / read threshold / write threshold** (for example 12/7/9). Each object is cut into `width` slices, one per Slicestor in the device set.
- Fewer than the **write threshold** of devices available means **writes to that vault fail**.
- Fewer than the **read threshold** means **data is unavailable**.
- **Maintenance margin = available devices − write threshold.** Before taking N devices offline (reboot, firmware, RMA, removal), count the devices that are **already** down, degraded or rebuilding in that set. For every vault on the set, the result must stay `≥ write threshold + 1`. That keeps one device of headroom for an unplanned failure during the work.
- Example: 12/7/9 with 1 device already down. 11 are available, so the margin is 2. Taking 1 more device offline keeps a margin of 1. Taking 4 offline means 7 available, below the write threshold: an **outage**.
- With Concentrated Dispersal (CD) mode, several slices sit on one Slicestor. Do the math per slice, not per node.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Site / device set / storage pool | Placement of Slicestors | Removing or replacing a device triggers data migration or rebuild. Set expansion is planned with IBM. |
| Vault (standard mode) / container vault + containers (container mode) | The bucket equivalent | IDA, storage pool and mode are fixed at creation |
| Vault template | Defaults for new vaults/containers | Changes affect every vault created from it later |
| Access pool / Accessers | S3 front-end | Removing an Accesser from a pool drops clients without a load balancer |
| Vault mirror | Two vaults kept in sync (often on two sites) | Breaking or deleting a mirror ends the protection |
| Vault proxy | Reads through to another S3 during migration | Removing it before migration completes hides data |
| Retention-enabled (protected) vault, legal holds, Object Lock | WORM / compliance | **Retention can't be disabled.** Objects under retention or legal hold can't be deleted early by anyone. |
| Versioning, quotas (soft/hard), name index | Vault features | A hard quota blocks writes. Without a name index there's no listing. |
| Users, roles, access keys | Super User, System Admin, Security Officer, Operator, **Read Only**. Access keys are per user, several allowed. | Deleting a key breaks the apps using it |

## Read-only (T0)
Manager REST API (Read Only user). Typical operations (confirm the names for your release):
- `viewSystem.adm`: the whole configuration (devices, sets, pools, vaults, access pools). The output is large, so filter it with `jq`.
- `listVaults.adm`, and the vault detail and usage operations
- device and event listing operations (device health, drive states, rebuilder status)
- usage and capacity reports per storage pool and vault

S3 through an Accesser, using a config-only profile:
```
aws --endpoint-url $EP s3api get-bucket-versioning --bucket V
aws --endpoint-url $EP s3api get-bucket-lifecycle-configuration --bucket V
aws --endpoint-url $EP s3api get-object-lock-configuration --bucket V      # if enabled on your release
aws --endpoint-url $EP s3api get-object-legal-hold --bucket V --key K      # retention vaults
aws --endpoint-url $EP s3api list-objects-v2 --bucket V --max-items 20 --query 'Contents[].{K:Key,S:Size,T:LastModified}'   # sample only
```
Never download object contents to "check" data, and never list whole vaults to get a size. Use the Manager's usage figures.

## Change operations by tier

| Tier | Operation | Notes / rollback |
|---|---|---|
| T1 | Create vault/container, user, access key, access pool member | Delete it (empty) to roll back. **IDA and storage pool are fixed at creation.** |
| T1 | Add a second access key (rotation start) | Delete the new key |
| T2 | Quota, vault ACL/policy, versioning enable, lifecycle without expiration, template changes | Record the old values |
| T2 | **Single device** maintenance mode / reboot / firmware, **within the IDA margin** | Bring it back online. Re-check vault health before the next device. |
| T3 | Taking devices offline beyond one at a time, removing a device from a set, replacing a device or Slicestor, set or pool changes | Do the IDA math for every vault on the set first. IBM support procedure. |
| T3 | Delete vault/container, empty a vault, delete objects in bulk, lifecycle expiration | **NONE** |
| T3 | Enable retention / Object Lock compliance, extend retention, set legal holds | Can't be undone or shortened |
| T3 | Delete access key / user, remove an Accesser from a pool, break or delete a vault mirror, remove a vault proxy | Apps or protection break |
| T3 | ClevOS upgrade (Manager-orchestrated rolling upgrade), Manager failover | IBM procedure, a maintenance window, and the IDA margin checked per set |

## Pre-checks every change needs
1. Exact identity: vault name and ID, device names and IDs, the device set, the storage pool, and **every vault on that set with its IDA**.
2. **Current health:** devices already offline, degraded, in maintenance or under RMA, drive failures, and **rebuilder** activity. Never stack maintenance on a set that is rebuilding unless the change is the fix.
3. Who uses it: access keys on the vault, recent request activity (Accesser logs / access-log vault), mirror and proxy relationships.
4. Protection: versioning, retention, legal holds, mirrors.
5. Capacity: storage pool used. A removed device's data must fit on the rest of the set.

## Rolling maintenance pattern (firmware, reboot)
1. Read all device states for the set and do the IDA math. The **maximum concurrency** is the margin minus 1 (keep one device of headroom). If the margin is 1 or already used up, nothing goes offline except the failed device.
2. Do one device per step:
   1. enter maintenance mode
   2. upgrade or reboot
   3. wait until it's online with healthy drives
   4. check that vault health is back to full width
   5. let the rebuilder catch up
   6. continue with the next device
3. Stop at the first device that doesn't come back cleanly.

"Faster" (several devices at once) is a T3 change that needs explicit IDA numbers in the plan, and it's never allowed beyond the margin.

## Retention vaults and erasure requests (GDPR)
- Retention can't be disabled, and the Super User can't force-delete objects under retention. The **Security Officer** role governs retention settings. Nobody can bypass an active retention period early.
- Legal holds can be released by authorized users, which unblocks deletion after the retention period expires.
- For an erasure request on a WORM vault, the answer is usually a legal one, not a technical one: legal obligations under the retention rule versus GDPR's exemptions for legal retention requirements. Check each object's retention expiry and holds and report them. Don't look for workarounds.
