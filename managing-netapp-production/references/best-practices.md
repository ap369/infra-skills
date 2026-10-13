# Best practices: configuration audit (ONTAP / StorageGRID)

Use this for a "best-practice audit" or "config review". Every check is read-only (T0) via `ontap_get` or the CLI. Each finding names the fix and its tier, and the fix goes through change-gate.md. Site standards override these defaults. Verify against NetApp TRs and Digital Advisor (Active IQ) wellness findings for your ONTAP release. **Digital Advisor's risk list is the first input to any audit.**

Report format: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Data protection and ransomware

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| N1 | Every production volume has a **snapshot policy** (not `none`) matching its RPO | Fast restore | `volume show -fields snapshot-policy` | T2 |
| N2 | **ARP/ARP-AI** enabled on NAS volumes (ARP/AI is active immediately from 9.16.1), FlexGroup (9.18.1) and SAN volumes (9.17.1). New volumes auto-enable from 9.18.1, so check that it wasn't turned off. | Early detection plus automatic snapshots | `security anti-ransomware volume show`, `security anti-ransomware auto-enable show` | T2 |
| N3 | **Tamperproof snapshots** (SnapLock-based snapshot locking) or Multi-Admin Verification (MAV) for critical volumes | Snapshots can't be deleted by a compromised admin | `volume show -fields snapshot-locking-enabled`, `security multi-admin-verify show` | T3 |
| N4 | **SnapMirror** to a second cluster for tier-1, with lag < 2× schedule. A vault policy (SnapVault) for long retention. | DR and backup | `snapmirror show -fields healthy,lag-time,policy` | T2 |
| N5 | SnapMirror destination volumes are type DP, with snapshot reserve and capacity sized for retention | Replication failures | `volume show -fields type` on the destination | T2 |
| N6 | SVM-DR or MetroCluster / SM active sync for apps that need RTO ≈ 0, with tested failover | RTO | `snapmirror show -type XDP`, `metrocluster show` | T3 |
| N7 | Restore tests (FlexClone from a snapshot or DR copy) at least quarterly | Untested backups don't count | process / recent clones | process |

## Capacity and efficiency

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| N8 | Aggregates **< 85%** used (AFF ≤ 85–90%, FAS lower), with forecast runway > 90 days | Performance, WAFL headroom | `storage aggregate show -fields percent-used` | plan |
| N9 | **Volume autosize** `grow` (or `grow_shrink`) with a sensible max, on volumes that hold LUNs or grow | Prevents LUN offline / ENOSPC | `volume show -fields autosize-mode,max-autosize` | T2 |
| N10 | Snapshot reserve sized so snapshots don't spill. **Snapshot autodelete** where appropriate (not on SnapMirror sources without care). | Space surprises | `volume show-space`, `volume snapshot autodelete show` | T2 |
| N11 | LUN volumes: thin provisioning **with** monitoring. `space-allocation` enabled for hosts that support UNMAP (the default for new LUNs from 9.15.1 only; **check older LUNs**). Fractional reserve 0 with autosize. | Reclaim, avoid offline LUNs | `lun show -fields space-reserve,space-allocation`, `volume show -fields fractional-reserve` | T2 |
| N12 | Storage efficiency (dedupe, compression, compaction) enabled on AFF (the default) | Capacity | `volume efficiency show` | T2 |
| N13 | Spare disks: at least 2 spares per disk type per node (or per NetApp's guidance for ADP) | Rebuild | `storage aggregate show-spare-disks` | hardware |

## High availability and networking

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| N14 | `storage failover show`: takeover possible on all HA pairs | HA | `storage failover show` | fix the cause |
| N15 | **Data LIFs on their home ports**, with failover groups/broadcast domains spanning both nodes of each HA pair | Non-disruptive failover | `network interface show -is-home false`, `-fields failover-group,failover-policy` | T3 (LIF) |
| N16 | SAN: **≥ 2 LIFs per node per fabric**, hosts with paths to both nodes of the HA pair, `selective LUN map` (SLM) as default | Path redundancy | `lun mapped show -fields reporting-nodes`, `network interface show -data-protocol fcp,iscsi` | T2 |
| N17 | Host utilities and multipath per the NetApp Interoperability Matrix (IMT). igroup `ostype` matches the host. | Supportability | `igroup show -fields ostype` | T2 |
| N18 | Jumbo frames consistent end to end for NFS/iSCSI, and LACP ifgrps on switches | Performance and stability | `network port show -fields mtu`, `ifgrp show` | network |

## Security

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| N19 | **Multi-Admin Verification** (9.11.1+) for destructive commands (volume/snapshot delete, recovery-queue purge, ARP pause/disable, lun delete), scoped with queries so automation isn't blocked. At least 2 approvers and a break-glass plan. | Insider and compromised-account protection | `security multi-admin-verify show` | T3 |
| N20 | Admin accounts via AD/LDAP with RBAC roles. `admin` vaulted. **MFA**: SSH TOTP (9.13.1), Duo (9.14.1) or FIDO2/PIV (9.12.1). System Manager via SAML IdP or WebAuthn (9.16.1). No MD5 password hashes. | Accountability | `security login show` | T2 |
| N21 | **Read-only role** for monitoring and MCP (ontap-mcp started with `--read-only`) | Blast radius | `security login show -role readonly`, MCP flags | T2 |
| N22 | NFS export rules least privilege: no `0.0.0.0/0` rw, superuser `none` unless needed. Encryption in flight with Kerberos (krb5p) or **NFS over TLS 1.3 (9.19.1)**. | Data exposure | `vserver export-policy rule show` | T2 |
| N23 | SMB: signing/encryption per policy, SMB1 disabled | Security | `vserver cifs options show`, `cifs security show` | T2 |
| N24 | NAE/NVE encryption with external or onboard key manager, keys backed up | Compliance | `volume show -fields encrypt`, `security key-manager show` | T3 |
| N25 | Audit logging forwarded to a SIEM (`cluster log-forwarding`), NTP on all nodes, AutoSupport on | Detection, support | `cluster log-forwarding show`, `cluster time-service ntp server show`, `autosupport show` | T2 |
| N26 | ONTAP on a **recommended** release (not EOS). Firmware per Digital Advisor. | Bugs, security | `version`, Digital Advisor | T3 |

| N27 | **JIT privilege elevation** (9.17.1+) for admin work: users and tools are read-only by default and elevate for a bounded window | Least privilege for humans and agents | `security jit-privilege show`, `security jit-privilege user show` | T2 |
| N28 | **TLS 1.0/1.1 disabled.** Upgraded clusters keep them enabled, unlike new installs. HSTS on (default from 9.17.1). | Protocol security | `security config show` | T2 |
| N29 | Audit log forwarded with `-protocol tcp-encrypted`, and tamper alerts reviewed (9.12.1+) | Detection, tamper evidence | `cluster log-forwarding show` | T2 |
| N30 | Netlogon AES enabled on SVMs created before 9.14.1 (an upgrade doesn't change it) | SMB security | `cifs security show -vserver S -fields aes-enabled-for-netlogon-channel` | T2 |
| N31 | Degraded aggregates alerted on. Since 9.12.1 ONTAP no longer shuts the controller down after 24h, so a degraded RAID group can go unnoticed. | Durability | `storage aggregate show-status`, `system health alert show` | hardware |

## StorageGRID

| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| G1 | ILM keeps **≥ 2 copies or EC across sites** for production tenants, simulated and documented | Durability | `/grid/ilm-policies`, `/grid/ilm-rules` | T3 |
| G2 | **S3 Object Lock** on backup-target buckets (Veeam, Commvault, ...) | Ransomware-proof backups | tenant `/org/containers/{b}/object-lock` | T3 |
| G3 | Per-tenant quotas, keys per application, no root-account keys in apps | Blast radius | `/grid/accounts`, tenant users | T2 |
| G4 | Storage < 80% per site, ILM backlog near zero | Headroom | metrics | plan |
| G5 | HA groups for gateway / load balancer endpoints, trusted certs | Availability | `/private/ha-groups`, endpoints | T2 |
