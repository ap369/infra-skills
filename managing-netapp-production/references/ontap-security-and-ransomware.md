# ONTAP security: ARP/AI, MAV, JIT, MFA, audit

Source: *ONTAP 9 documentation* PDF (2026-10-08). `pN` = PDF page. Every **enable / modify / disable / clear-suspect / restore** below is a change and goes through change-gate.md. The tiers given are this skill's tiers.

## Autonomous Ransomware Protection (ARP, ARP/AI)

### Behaviour by version (p2297, p2328, p2300)
| Volume type | Version | Behaviour on enable |
|---|---|---|
| NAS FlexVol | 9.10.1–9.15.1 | Learning mode for 30 days. From 9.13.1, adaptive learning switches to active on its own. |
| NAS FlexVol | **9.16.1+** | **ARP/AI active immediately**, no learning |
| FlexGroup | 9.13.1–9.17.1 | First-generation ARP, with learning |
| FlexGroup | **9.18.1+** | ARP/AI, active immediately |
| SAN (LUN / NVMe namespace) | before 9.17.1 | Not supported |
| SAN | **9.17.1+** | ARP/AI with an entropy **evaluation period** to set the threshold. Only volume-level entropy: **no suspected-file lists**. |
| Default for new volumes | **9.18.1+** | Auto-enabled after a 12h grace period on supported platforms (AFF A/C, ASA, ASA r2) |

### Commands (read: T0 · change: T2 unless noted)
- Read:
  - `security anti-ransomware volume show [-vserver S -volume V]`
  - `security anti-ransomware auto-enable show`
  - `security anti-ransomware volume entropy-stat show-recent-high-encryption-stat -vserver S -volume V`
  - `security anti-ransomware volume entropy-stat show-encryption-percentage-histogram -vserver S -volume V`
  - `security anti-ransomware volume attack-detection-parameters show`
  - EMS: `event log show -message-name callhome.arw.activity.seen`
- Enable: `security anti-ransomware volume enable -vserver S -volume V` (T2). Default for new volumes: `security anti-ransomware auto-enable modify -new-volume-auto-enable true|false` (T2).
- **Pause / disable** (`security anti-ransomware volume pause|disable`): **T3**, because it weakens protection. Protect it with MAV.
- Tuning (T2): `attack-detection-parameters modify`, `workload-behavior clear-surge` (report a known surge as normal), `safe-extension-list add|remove`, `event-log modify` (alerts on a new extension or an ARP snapshot, 9.14.1+).

### ARP snapshots (p2315–2316)
| Name prefix | Version | Purpose / retention |
|---|---|---|
| `Anti_ransomware_periodic_backup.*` | 9.17.1+ | Taken every 4 hours. **Normal, not an anomaly.** |
| `Anti_ransomware_attack_backup.*` | 9.17.1+ | Taken on an anomaly. Default retention 10 days. |
| `Anti_ransomware_backup.*` | ≤ 9.16.1 | Taken on an anomaly |

After clear-suspect, ARP snapshots are kept for **7 days if marked a real attack, 24h if marked a false positive** (9.17.1+). In 9.16.1 it was 5 days / 48h. **In 9.15.1 and earlier, clear-suspect deletes the ARP snapshots immediately** (p2344).

### Responding to an ARP alert (p2312–2317)
1. **Don't delete snapshots and don't restore yet.** Read the alert, the entropy stats, and the suspected file types (NAS only).
2. NAS: generate the attack report first with `security anti-ransomware volume attack generate-report -vserver S -volume V -dest-path S:/path` (T1, writes a file).
3. **Classify** (T2, MAV may require approvals), with `-false-positive false` for a real attack or `true` for a false positive:
   - NAS extensions: `security anti-ransomware volume attack clear-suspect -vserver S -volume V [-extension ...] -false-positive true|false`
   - Entropy spike (NAS and SAN; **the only way on SAN**): `... clear-suspect -vserver S -volume V -start-time "MM/DD/YYYY HH:MM:SS" -end-time "..." -false-positive true|false`
   - 9.18.1+: check the outcome with `security anti-ransomware volume show -clear-suspect-status -vserver S -volume V`
4. **The order depends on the restore method and version:**
   - **Volume snapshot restore, 9.16.1+:** run clear-suspect **first**, then restore. Clear-suspect isn't available after a volume restore.
   - **Volume snapshot restore, ≤ 9.15.1:** restore **first** (clear-suspect deletes the ARP snapshots).
   - **FlexClone or single-file SnapRestore** (preferred, narrower): recover the data first, then clear-suspect.
   - Restoring from an **earlier** snapshot than the latest ARP one needs the lock released (clear-suspect with `false-positive false`) first. FlexClone and file restore don't need that.
5. **SnapMirror:** if the volume is replicated, update all mirrors manually after a volume restore. For SnapMirror sync / active sync SAN on 9.19.1, quiesce or break before a volume restore, then re-protect (p2316).
6. Engage security and incident response (references/incident-comms.md). Keep the attack report.

## Multi-admin verification (MAV) (p2173–2212)
- **What it does:** protected operations (volume/snapshot delete, ARP pause/disable, SnapLock ops, login changes and more) need approval from an approval group. MAV rules are evaluated **after RBAC**. Approvers also need the RBAC privileges.
- **Always protected once enabled:** MAV configuration itself, plus `security login password`, `security login unlock` and `set` by default. Many more commands can be added per release (the list is version-specific, p2175+).
- **Setup** (T3, typed confirmation, needs two named approvers and a break-glass plan):
  1. `security multi-admin-verify approval-group create -name G -approvers u1,u2 [-email ...]` (admin SVM only)
  2. `security multi-admin-verify rule create -operation "volume delete" [-query "..."]`
  3. `security multi-admin-verify modify -approval-groups G -required-approvers 1 -enabled true [-execution-expiry 1h] [-approval-expiry 1h]`
- **Request flow:**
  1. The user runs the protected command, which auto-creates a request.
  2. An approver runs `security multi-admin-verify request show-pending` / `request show N` / `request approve N` (or `request veto N`).
  3. The user re-runs the command within the execution expiry.
- **Gotchas:**
  - Disabling MAV needs MAV approval. If no approver is available, NetApp Support has a KB procedure.
  - **Not for heavily automated workflows.** Scope rules with queries (for example, exclude automation-named volumes or `-snapshot !hourly*,!daily*`).
  - Not available on Cloud Volumes ONTAP.
- **Agent rule:** Claude never approves its own requests and never asks the user for approver credentials. An approver approves with their own identity.

## JIT privilege elevation (9.17.1+, p2144–2147)
- Lets users temporarily take a higher RBAC role (default `admin`) inside **one SSH session**. This fits the skill's read-only-by-default model: the agent's user stays read-only, and a human grants a JIT window for an approved change.
- **Limits:** SSH only. Works only with password, nsswitch or domain authentication. **Not with MFA.**
- Global defaults: session validity **1h**, max JIT validity **90 days** (`security jit-privilege show [-vserver S]`, `security jit-privilege modify -vserver S ...`).
- Grant (T2): `security jit-privilege user create -username U -role R -session-validity-period 1h -jit-validity-period 1d -start-time "..."`. Review with `security jit-privilege user show`, revoke with `security jit-privilege user delete`.
- The user runs `security jit-privilege elevate`, checks time with `security jit-privilege show-remaining-time`, and ends early with `security jit-privilege reset`.
- For agent use: grant the shortest validity that covers the approved window, and revoke it right after the post-checks.

## Authentication hardening
- **MFA:**
  - SSH: FIDO2/PIV YubiKey (9.12.1), TOTP (9.13.1), Cisco Duo (9.14.1)
  - System Manager: SAML IdP (Duo from 9.9.1), **WebAuthn** (9.16.1, with `-rp-domains` restriction from 9.19.1)
  - SSH certificate validation (9.13.1), dynamic authorization by trust score (9.15.1, run visibility mode before enforced)
- Accounts still using MD5 password hashes: lock them with `security login expire-password -vserver * -username * -hash-function md5 -lock-after N` (advanced), and have users reset their passwords (p2173).
- Since 9.16.1, cluster admin accounts can use AD without an authentication tunnel (`vserver active-directory create` on the admin SVM). Before 9.16.1, `security login domain-tunnel create` is needed (p2165).
- **TLS:** TLS 1.0/1.1 stay enabled on upgraded clusters, so disable them deliberately. HSTS is on by default from 9.17.1. NFS over TLS 1.3 from 9.19.1. NVMe/TCP TLS from 9.16.1.

## Audit logging (p3170–3176)
- Read with `security audit log show [...]` (merged across nodes). Configure what's audited with `security audit show` / `security audit modify` (GET auditing; cross-cluster GETs from 9.17.1).
- **Forward to a SIEM** with `cluster log-forwarding create -destination <host> -port 6514 -protocol tcp-encrypted -facility user` (T2; it validates the destination certificate, p3175). Don't use `-force` to skip the connectivity check. Pin the source LIFs with the management-log-forwarding service (9.12.1). EMS to syslog over TLS has been possible since 9.12.1 (p3234).
- **Tamper alerts** on audit logs since 9.12.1.
- NAS file auditing (SMB/NFS events) and FPolicy are separate features. See the "Audit NAS events on SVMs" chapter.
