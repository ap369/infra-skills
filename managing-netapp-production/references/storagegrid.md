# StorageGRID reference (11.x)

APIs: Grid Manager `https://<admin-node>/api/v4/...` (grid-wide). Tenant Manager uses the same API, scoped to one tenant account. Confirm the version with `/api/versions`.

## Object model

| Object | What it is | Gotchas |
|---|---|---|
| Grid / site / node (admin, gateway, storage, archive) | Distributed object store | Node decommission and site removal are permanent |
| Tenant account | S3/Swift tenancy, quota | Deleting a tenant requires empty buckets |
| Bucket | S3 bucket; versioning, Object Lock, CloudMirror | Object Lock compliance can't be undone |
| ILM policy & rules | Where copies live, how many, and for how long | **The highest-risk object.** Activating a policy re-evaluates *every* object grid-wide, and can delete or move data. |
| Storage pool / EC profile | Placement targets for ILM | Changing one affects all the rules that use it |
| Load balancer endpoint / HA group | Client entry points | Changes drop client connections |
| Platform services (CloudMirror, notifications, search) | Per-bucket integrations | Endpoint errors pile up silently |

## Read-only (T0)
Grid API GET:
- `/grid/health`, `/grid/alerts` (current alerts), `/grid/node-health`
- `/grid/sites`
- `/grid/accounts` (tenants, with `usage`)
- `/grid/ilm-policies`, `/grid/ilm-rules`
- `/grid/storage-pools`, `/grid/ec-profiles`
- `/private/load-balancer-endpoints`, `/private/ha-groups`
- metrics via `/grid/metric-query` (Prometheus queries)

Tenant API GET: `/org/containers` (buckets), `/org/containers/{bucket}/versioning`, `/org/containers/{bucket}/object-lock`, `/org/usage`.

## Change operations by tier

| Tier | Operation | Notes / rollback |
|---|---|---|
| T1 | Create tenant / bucket / access key | Delete it to roll back (bucket must be empty) |
| T2 | Tenant quota | Lowering it below usage blocks writes |
| T2 | Bucket versioning enable/suspend, lifecycle config | A lifecycle rule can expire data in bulk |
| T2 | Load balancer endpoint / HA group / certificate | Clients reconnect. Test the cert chain first. |
| T2 | Platform service endpoint | Verify the endpoint before attaching it |
| T3 | **Activate an ILM policy or edit a rule used by the active policy** | **Simulate first** (Grid Manager "simulate" with real object names). Get the data owner's sign-off. Assess the re-evaluation load. Rollback means re-activating the previous policy, but objects already deleted are gone. |
| T3 | Delete bucket / objects / tenant | Irreversible unless versioning or Object Lock protects them |
| T3 | Enable Object Lock (compliance), set default retention | Can't be disabled or shortened |
| T3 | Delete access key / tenant user | Apps break immediately |
| T3 | Node decommission, site decommission, storage volume removal, expansion, recovery | NetApp Support / documented procedure only |

## Pre-checks
- Grid health, open alerts, and node-health all green before any change.
- For ILM: list the active policy and rules, the affected tenants and buckets, object counts, and copies per site. Make sure no other ILM evaluation backlog is in progress.
- For buckets: versioning, Object Lock, CloudMirror, lifecycle config, and recent client activity (audit logs and metrics).
