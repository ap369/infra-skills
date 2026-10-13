# PowerMax security, access roles and versions (from Dell public documentation)

Sources (public PDFs at dl.dell.com, retrieved 2026-10-14):
- *PowerMax Family Security Configuration Guide, PowerMaxOS 10* (Apr 2026)
- *Solutions Enabler 10.4.0 Array Controls and Management CLI User Guide* (Apr 2026)
- *Solutions Enabler 10.4.0 Installation and Configuration Guide* (Apr 2026)
- *What is new in Solutions Enabler 10.4.0* (Oct 2025)
- *PowerMax Family Product Guide* (Apr 2026)
- *Events and Alerts for PowerMaxOS and HYPERMAX OS 10.3.0* (Oct 2025)

The PowerMaxOS and Solutions Enabler **release notes need a Dell login** and weren't used. Check them for your target code.

## Versions
- **Solutions Enabler 10.0 or later is required to discover arrays running PowerMaxOS** 10 (Security Config Guide). Keep SE/Unisphere at or above the array's supported level. Latest documented: SE 10.4.0, Unisphere 10.4.0, PowerMaxOS 10.4.
- **New in SE 10.4:**
  - `symprov add` supports NVMe/TCP and iSCSI endpoints
  - `symlmf register|deregister -sid S` for connected (cloud) eLicensing
  - `symmdr ... modify -cascaded` for Metro Smart DR
  - no SnapVX CLI changes

## Solutions Enabler access-control roles (symauth)
| Role | Rights |
|---|---|
| None | No rights |
| **Monitor** | Read-only operations, **excluding** the audit log and access-control definitions. **Use this for agents and monitoring.** |
| PerfMonitor | Monitor + performance alert/threshold setup in Unisphere |
| Auditor | Monitor + read the audit log |
| LocalRep | Local replication (SnapVX) |
| RemoteRep | Remote replication (SRDF) |
| DeviceManage | Device control and configuration operations |
| StorageAdmin | All management operations (SGs, devices, GNS) + monitor |
| SecurityAdmin | `symaudit`, `symacl`, `symauth` + Auditor rights. Can create or delete component authorization rules. |
| MainframeAdmin | CKD map/unmap and CU controls (PowerMaxOS 10.1+) |
| Admin | Everything, including security |

The narrowest write identity for a change window is LocalRep, RemoteRep or DeviceManage, scoped to what the plan needs, rather than StorageAdmin or Admin.

## Security checklist (Security Configuration Guide)
- **Solutions Enabler:**
  - restrict which hosts can run which actions (**symacl** access-control groups, pools and hosts) and which users (**symauth**)
  - prefer **client/server mode** to a `storsrvd` on a locally attached host, so fewer hosts need gatekeepers
  - encrypt client/server traffic with TLS, ideally with custom certificates
  - protect the **lockbox** (stable system values, password management)
  - secure daemon identities and directories
  - keep the SE audit log
- **Unisphere:**
  - authenticate through **LDAP-TLS**
  - give each user the **minimum role**
  - **replace the pre-generated TLS certificates**
  - set session inactivity timeouts
  - MFA via **RSA SecurID** or **YubiKey**, or SSO via **OIDC**
  - use the security alert system and CyberSecIQ
- **Data at rest encryption (D@RE)** with an internal or external key manager, per policy.
- **Code signing:** verify the signatures of downloaded software before installing.

## Thin device deallocation (`free -all`), Array Controls guide
- `symdev -sid S free -devs <range> -all` (also `symsg ... -sg SG` / `symdg ... -g DG`) frees **all allocations, including written tracks**. **Dell: "can result in lost data."**
- The device must be **unmapped or Not Ready**. **`free -all` is blocked on devices in replication.**
- While a background free runs on a Ready device, RDF createpair, map, convert and all TimeFinder operations are refused on it. Stop it with `-stop`.
- The skill keeps this as **stage 2 only** of the decommission pattern (after unmask and quarantine).

## Documented command forms to use (corrections)
| Don't write | Write |
|---|---|
| `symsg -sg SG set -slo <SL>` | `symsg -sg SG -sid S set -sl <SL> [-wl <workload>]` (Diamond on All Flash. Other SLs apply to hybrid VMAX3. PowerMaxOS 10 service-level behaviour per the release docs.) |
| `symdisk list -failed` | `symdisk list -sid S -v` / `symdisk list -sid S -state ...` / `-dskgrp_summary`, and Unisphere hardware health |
| `symdev list -noport` | Find unmapped devices with Unisphere or `symsg list` / `symaccess list view`. The `-noport` filter isn't in the user guides; check `symdev list -h`. |
| `symstat ...`, `symgate list` | Real SE commands, but documented only in the online CLI Reference (developer.dell.com), not in the PDFs used. Check `-h` before use. |
