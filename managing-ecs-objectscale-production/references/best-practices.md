# Best practices: configuration audit (ECS / ObjectScale)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0): Management API GETs as System Monitor and `s3api get-*` with the config-only profile. Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify against Dell's ECS best-practices and security configuration guides for your release.

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Data protection

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| E1 | Production namespaces and buckets in a **geo replication group** (≥ 2 VDCs), unless documented as single-site | Site loss | bucket info `vpool`, `/vdc/data-service/vpools` | new bucket (RG is fixed) |
| E2 | Geo **RPO monitored** and within the target | DR | replication group dashboard | T2 |
| E3 | **Versioning + Object Lock** (or bucket retention) on backup-target buckets (Veeam, Commvault, NetBackup, ...), in the mode the backup vendor recommends | Ransomware-proof backups | `get-bucket-versioning`, `get-object-lock-configuration` | T3 |
| E4 | ADO (access during outage) set **deliberately** per bucket: on for availability-first apps, off where strong consistency matters | Consistency vs. availability | bucket info `is_stale_allowed` / ADO flags | T2 |
| E5 | Lifecycle rules on versioned buckets include `NoncurrentVersionExpiration` and `AbortIncompleteMultipartUpload` | Silent capacity growth | `get-bucket-lifecycle-configuration` | T2 |
| E6 | Compliance namespaces and retention classes used only where legally required, and documented | Irreversible capacity commitment | namespace info | T3 |

## Capacity and performance

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| E7 | Storage pools **< 75–80%** used, with headroom for GC, erasure coding and node-failure rebuild | Writes can stall at high fill | `/dashboard/zones/localzone`, `/object/capacity` | plan |
| E8 | GC healthy (reclaimable space draining) | Capacity | GC metrics | report |
| E9 | **Quotas** (namespace and bucket) on multi-tenant systems, with soft-quota alerts | Noisy tenants | namespace and bucket quota | T2 |
| E10 | A load balancer in front of data nodes (health checks on 9021/9020), with no clients pinned to one node's IP | Availability | LB config | network |
| E11 | Large-object clients use multipart upload. Many-small-object workloads are reviewed for overhead. | Performance | app review | app |

## Security

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| E12 | Management users via AD/LDAP. **System Monitor** for monitoring and tools. Root/default accounts vaulted. | Accountability | `/vdc/users` | T2 |
| E13 | One object user per application, keys rotated (two-key overlap), no shared keys | Blast radius, rotation | `/object/users`, key timestamps (metadata only) | T1/T2 |
| E14 | Bucket policies **least privilege**: no `Principal: "*"`, no public read unless intended and documented | Data exposure | `get-bucket-policy` | T2 |
| E15 | HTTPS only (9021) with trusted certs on the data and management planes. HTTP 9020 disabled or firewalled. | Credentials in transit | cert info, LB/firewall | T2 |
| E16 | D@RE (data at rest encryption) enabled where required, with KMS per policy | Compliance | namespace / bucket encryption flags | T3 |
| E17 | Audit/event logs forwarded to SIEM (syslog), NTP consistent across nodes | Detection | syslog config, `/vdc/nodes` | T2 |
| E18 | ECS/ObjectScale on a supported release, upgrades with Dell, Secure Connect Gateway connected | Bugs, support | version, ESRS/SCG | T3 |
