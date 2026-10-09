# Upgrades and migration: ECS / ObjectScale

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against Dell's ECS / ObjectScale upgrade guides for your release.

## ECS upgrades
- **How:** Dell-led or Dell-assisted rolling upgrades, node by node. Federated systems go **one VDC at a time**.
- **Extra readiness checks:**
  - Dell's pre-upgrade health checks are clean (xDoctor-style health report)
  - nodes and disks healthy, no rebalancing or data recovery in progress
  - geo replication caught up (RPO normal) before you take a VDC through an upgrade
  - capacity headroom (best-practices.md E7): a node down shifts load and needs room
  - the load balancer health checks remove the node being upgraded from rotation
- **Watch:**
  - node returns
  - LB re-adds it
  - S3 error rate (5xx) and latency normal
  - geo RPO recovers

## Migration / tech refresh
Options:
1. **ECS → ObjectScale (Dell-supported path):** follow Dell's procedure for your source and target versions.
2. **S3-to-S3 copy** (to new ECS, ObjectScale or another S3): copy tools that preserve metadata and **versions**, and parallelize by prefix. Verify object counts and checksums per bucket.
   - **Object Lock / retention:** locked objects can't be deleted at the source until expiry. Recreate the lock config on the target **before** copying, and set per-object retention to the remaining period, not a fresh full period.
3. **App-level:** point the app at the new endpoint with dual-write or read-through during transition, where the app supports it.

**Checklist for any migration:**
- inventory: namespaces, buckets, owners, policies, versioning, lock and retention, lifecycle, quotas, users and keys (metadata only), CAS/NFS-enabled buckets (special handling)
- client endpoints and DNS
- cutover per tenant
- rollback: the source untouched until sign-off
- decommission with the bucket pattern in ecs.md
