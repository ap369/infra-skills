# Upgrades and migration: IBM COS (Cleversafe)

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against IBM's ClevOS upgrade documentation for your release.

## ClevOS upgrades
- **How:**
  - orchestrated from the Manager, **Manager first**, then Accessers and Slicestors in rolling batches
  - the batch size is **limited by the IDA margin** of every vault on each device set (ibm-cos.md)
  - IBM support involvement per your contract
- **Extra readiness checks:**
  - IDA margin math per device set, **counting devices already down**. Max concurrent devices = margin − 1.
  - no rebuilder backlog, no device in a degraded state, no drives failed and pending replacement
  - Accesser pools behind a load balancer, so one Accesser at a time drains cleanly
  - Manager backup taken (best-practices.md C20)
- **Watch per device:**
  - device online
  - drives healthy
  - vault health back to full available width
  - rebuilder caught up
  - S3 error rate normal

## Migration / tech refresh
Options:
1. **Hardware refresh within dsNet:** add new device sets or storage pools, migrate vaults per IBM's procedure, and retire old devices (IBM-led, IDA-aware).
2. **Vault proxy (read-through):** clients write to the new vault, reads fall through to the legacy source until a background copy completes. Don't remove the proxy before the copy is verified.
3. **S3-to-S3 copy** to another system: preserve versions and metadata, recreate retention or Object Lock on the target **first**, and verify counts and checksums.

**Checklist for any migration:**
- inventory: vaults (IDA, pool, mode), versioning, retention/legal holds, lifecycle, quotas, users and keys (metadata only), mirrors, proxies
- target IDA and site design reviewed (best-practices.md C1/C2)
- cutover per tenant/app
- rollback: the source untouched until sign-off
- decommission with the vault pattern in ibm-cos.md
