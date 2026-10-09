# Best practices: configuration audit (IBM COS / Cleversafe dsNet)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0): Manager `view*`/`list*` as the Read Only user and `s3api get-*` with the `cos-ro` profile. Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify against IBM's COS (dsNet) configuration and security guides for your ClevOS release.

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Durability and availability (IDA design)

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| C1 | **IDA margin ≥ 2** (width − write threshold) on production vaults, so one device can be in maintenance while another fails | Maintenance without outages | vault IDA from `viewSystem` / `listVaults` | new vault (IDA is fixed) |
| C2 | Multi-site deployments: IDA and site layout tolerate the **loss of one full site** (slices per site ≤ width − read threshold for reads, and ≤ width − write threshold if writes must survive) | Site loss | device set site placement | design (IBM) |
| C3 | **No device set running degraded** for long: failed drives replaced promptly, RMAs tracked | The margin silently erodes | device and drive states | hardware |
| C4 | Rebuilder healthy (backlog draining) | Durability | rebuilder status | report |
| C5 | Vault mirrors (or a second system) for data that needs site-level DR beyond the IDA | DR | mirror config | T2/T3 |
| C6 | Concentrated Dispersal (CD) mode only where intended, with its per-node slice math documented | Hidden margin loss | vault/pool mode | design |

## Protection and data management

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| C7 | **Versioning + retention / Object Lock** on backup-target vaults (Veeam, Commvault, Spectrum Protect, ...) in the mode the vendor recommends | Ransomware-proof backups | `get-bucket-versioning`, retention/lock config | T3 |
| C8 | Retention-enabled vaults only where legally required. Retention defaults and limits documented, and the Security Officer role separated from admins. | Irreversible, governance | vault retention settings, role assignments | T3 |
| C9 | Lifecycle rules on versioned vaults expire noncurrent versions and incomplete multipart uploads | Silent capacity growth | `get-bucket-lifecycle-configuration` | T2 |
| C10 | Name index enabled on vaults that need listing (S3 ListObjects), and a deliberate decision on others | App behavior | vault config | T2 at creation |
| C11 | Quotas (soft/hard) per vault on multi-tenant systems | Noisy tenants | vault quotas | T2 |

## Capacity and performance

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| C12 | Storage pools **< 80%** used, with expansion planned (set expansions take lead time) | Headroom | pool usage | plan |
| C13 | Accessers in access pools **behind a load balancer** with health checks, at least N+1 | Availability | access pool members | network |
| C14 | Clients use multipart for large objects, and reasonable object sizes | Efficiency | app review | app |

## Security and management

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| C15 | Manager accounts via LDAP/AD. **Read Only** for monitoring and tools. Super User vaulted. Security Officer separated. | Accountability | user/role listing | T2 |
| C16 | Access keys per application, rotated, no shared keys | Blast radius | user access-key metadata | T1/T2 |
| C17 | HTTPS only on Accessers, with trusted certs. The Manager on a management network. | Credentials in transit | certs, network | T2 |
| C18 | Encryption: SecureSlice/encryption settings per policy | Compliance | vault settings | design |
| C19 | Event forwarding (syslog/SNMP) to monitoring/SIEM, NTP on all devices | Detection | Manager alert/syslog config | T2 |
| C20 | **Manager backups** configured and tested (Manager config is critical) | Recoverability | Manager backup config | T2 |
| C21 | ClevOS on a supported release, all devices on the same version outside upgrades | Bugs, support | device versions | T3 |
