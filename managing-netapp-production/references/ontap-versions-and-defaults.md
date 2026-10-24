# ONTAP versions, features and defaults

> **Command verification status:** ONTAP CLI forms in this skill were cross-checked against NetApp's *ONTAP 9 documentation* (2026-10-08, ONTAP 9.19.1). Commands listed in ontap-command-catalog.md, and ones that match it, are `[doc]`. Any other form, or a new parameter, is `[unverified]`. Confirm parameters on the target with `<command> ?` before use. See command-verification.md.


Source: *ONTAP 9 documentation* PDF (NetApp, generated 2026-10-08, covers up to 9.19.1). `pN` = PDF page. Always check the live version first (`version`, `cluster image show`). A feature is only usable when **every** node runs the release that introduced it, because the cluster version is the lowest node version (p302).

## Release support policy (p148–149)
- A new release gets **3 years of full support**, then limited support, then self-service.
- NetApp recommends **running the newest release for about 1 year after GA**, then planning the move within the support window.
- **Patches (P-releases):** apply non-critical ones every 3–6 months and critical ones as soon as possible.
- Releases older than 9.10.1 are probably on limited or self-service support. Flag them in audits.
- `9.x.0` releases are cloud-only (Cloud Volumes ONTAP). The exception is 9.16.0, which is for ASA r2. `9.x.1` releases are general on-prem releases (p226).

## Feature → first release (operational subset)

| Area | Feature | Since | p |
|---|---|---|---|
| Ransomware | ARP (NAS, learning mode 30 days) | 9.10.1 | 2330 |
| Ransomware | ARP on SnapMirror async destination volumes | 9.12.1 | 2294 |
| Ransomware | ARP adaptive learning (switches to active automatically) | 9.13.1 | 2334 |
| Ransomware | ARP alerts on new file extension / ARP snapshot creation | 9.14.1 | 2306 |
| Ransomware | **ARP/AI:** pre-trained model, **active immediately on NAS FlexVol**, no learning | 9.16.1 | 2283, 2298 |
| Ransomware | **ARP/AI on SAN volumes** (entropy-based, with an evaluation period); periodic 4-hour ARP snapshots | 9.17.1 | 2299, 2290 |
| Ransomware | ARP/AI on FlexGroup (default model). **Enabled by default on new volumes** after a 12h grace period (AFF A/C, ASA, ASA r2) | 9.18.1 | 2285, 2288, 2300 |
| Ransomware | ARP/AI on SnapMirror synchronous (NAS/SAN) and active sync SAN primaries | 9.19.1 | 2294 |
| Admin security | Multi-admin verification (MAV) | 9.11.1 | 2173 |
| Admin security | MAV for SnapLock ops; AD users as MAV admins (9.15.1); MAV for consistency groups (9.16.1) | 9.13.1 | 2763, 2198, 2801 |
| Admin security | SSH MFA with YubiKey (FIDO2/PIV) | 9.12.1 | 2128 |
| Admin security | SSH MFA with **TOTP** | 9.13.1 | 2129 |
| Admin security | Cisco Duo for SSH | 9.14.1 | 2153 |
| Admin security | Dynamic authorization (trust score for SSH users) | 9.15.1 | 2214 |
| Admin security | WebAuthn MFA for System Manager | 9.16.1 | 2259 |
| Admin security | **JIT privilege elevation** (SSH, temporary role) | 9.17.1 | 2144 |
| Admin security | HSTS for web services (default on new clusters) | 9.17.1 | 2271 |
| Audit | Tamper alerts for audit logs; audit forwarding over TLS (EMS) | 9.12.1 | 3170, 3229 |
| Audit | Cross-cluster GET auditing | 9.17.1 | 3174 |
| Snapshots | **Tamperproof snapshot locking** (`-snapshot-locking-enabled`) | 9.12.1 | 2794 |
| Snapshots | Snapshot locking on SnapLock vault / SnapMirror destinations (long-term retention) | 9.14.1 | 2793 |
| Snapshots | Snapshot locking expiry can be set only at snapshot creation | 9.19.1 | 2794 |
| SnapMirror | SVM-DR reverse resync with `-quick-resync` | 9.11.1 | 2736 |
| SnapMirror | quick-resync attempted by default (no clones, MirrorAllSnapshots) | 9.13.1 | 2706 |
| SnapMirror | Per-relationship `-backoff-level`; app snapshots replicate without a label | 9.14.1 | 2677, 2641 |
| SnapMirror | Sync: scheduled snapshot replication; snapshot delete/rename/modify replicated | 9.19.1 | 2642 |
| SnapMirror | SnapMirror Cloud: up to 100 buckets per cluster | 9.19.1 | 2755 |
| Active sync | Symmetric active/active on 4-node clusters | 9.16.1 | 2855 |
| Active sync | NVMe support; ONTAP Cloud Mediator (can't be combined with on-prem Mediator) | 9.17.1 | 2856, 2859 |
| Active sync | **NAS support** (SVM level, NFS v3/v4, SMB; 2-node AFF only; no direct SVM-DR conversion) | 9.19.1 | 2832, 2888, 2891 |
| Consistency groups | CLI management; SVM-DR support for CGs | 9.14.1 | 2799, 2817 |
| Mobility | SVM migrate (`vserver migrate`) | 9.10.1 | 639 |
| SAN | Space allocation default on for new LUNs and namespaces | 9.15.1/9.16.1 | 73, 1934 |
| SAN | NVMe/TCP TLS secure channel | 9.16.1 | 1914 |
| SAN | Direct-attached FC / FC-NVMe on certain systems; SAN active-active LIF failover (AFF) | 9.19.1 | 1960, 1060 |
| SAN | iSCSI support in Foreign LUN Import (FLI) | 9.19.1 | 23 |
| NAS | **NFS over TLS 1.3** (must be disabled before a revert) | 9.19.1 | 1288, 327 |
| S3 | Bucket lifecycle (expiration) rules | 9.13.1 | 2028 |
| S3 | S3 bucket snapshots (9.16.1); native snapshot restore of a whole bucket (9.18.1) | 9.16.1 | 2089, 2094 |
| S3 | **Second access key per user** (rotation without downtime); conditional writes/deletes | 9.19.1 | 2034, 1994 |
| QoS | Adaptive QoS at SVM level (9.13.1); nested QoS (9.18.1); burst policies (9.19.1) | | 105, 3148, 3141 |
| Upgrade | `cluster image validate` shows errors and warnings separately | 9.19.1 | 151 |
| Upgrade | ANDU keeps newer pre-staged BIOS/LOADER firmware | 9.17.1 | 324 |
| Encryption | NVE on SVM root volume (blocks revert to ≤ 9.13.1 until converted) | 9.14.1 | 2535, 327 |
| HA / cluster | HA traffic encryption (9.18.1); backend cluster network TLS (9.18.1) | 9.18.1 | 676, 1120 |

## Default changes that affect operations (p72–73)

| Release | Default change | Audit / ops impact |
|---|---|---|
| 9.18.1 | ARP/AI auto-enabled on all new volumes after a 12-hour grace period (supported platforms) | Check `security anti-ransomware auto-enable show`. Expect ARP snapshots and alerts on new volumes. |
| 9.17.1 | FSA (File System Analytics) on by default for volumes on new NAS SVMs | Small overhead. Useful for "who uses it" questions. |
| 9.17.1 | HSTS on by default | Browser and automation must use HTTPS |
| 9.17.1 | Cached positive credential TTL for SVMs cut from 24h to 1h | More name-service lookups. AD/LDAP outages show up faster. |
| 9.15.1 | Space allocation on by default for new LUNs | **Existing LUNs keep their old setting**, so audit N11 on older LUNs |
| 9.15.1 | `vserver object-store-server user show` no longer prints S3 secret keys | Good for transcripts. Older releases still print them, so don't run it there. |
| 9.15.1 | NAS audit keeps all records by default (rotate-limit revised) | Size the audit volume |
| 9.14.1 | AES on by default for Netlogon on **new** SVMs. Existing SVMs keep their setting after an upgrade. | Audit `cifs security show` on older SVMs (p2165) |
| 9.13.1 | AES on by default for Kerberos to SMB servers | |
| 9.12.1 | A degraded aggregate **no longer shuts the controller down after 24h** (unless `raid.timeout` is changed) | Nothing forces you to notice a degraded aggregate, so health checks must alert on it |
| 9.12.0 / 9.8 | TLS 1.1 / TLS 1.0 disabled on **new installs only**. Upgraded systems keep them enabled. | Audit: disable TLS 1.0/1.1 on upgraded clusters |

## Revert rules (p325–327)
- **Contact NetApp support before reverting a production cluster.** A revert is **disruptive** (no client access) and affects all nodes, one HA pair at a time.
- You can revert **only one release back per step** (9.15.1 → 9.14.1 → 9.13.1). Reverting to 9.4 or earlier isn't supported. **AFX systems can't revert.**
- Blockers to clear first:
  - NFS over TLS (9.19.1)
  - encrypted SVM root volumes (when going to ≤ 9.13.1)
  - LDAP referral
  - adaptive-compression volumes created on 9.5+
- In a mixed-version state, run only monitoring commands. Don't upgrade back mid-revert.
