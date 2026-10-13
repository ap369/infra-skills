# ONTAP documented command catalog

The commands below appear in the *ONTAP 9 documentation* PDF (2026-10-08). Prefer these forms in change plans, and still confirm parameters with `<command> ?` on the target release. The PDF doesn't include the full man-page reference, so a command missing here may still exist. **Read** = T0. Everything else is a change, tiered per SKILL.md.

## Corrections: use the documented form
| Don't write | Write |
|---|---|
| `lun mapped show` | `lun mapping show -vserver S [-path P]` |
| `lun unmap` | `lun mapping delete -vserver S -path P -igroup G` (T3) |
| `lun online` | `lun modify -vserver S -path P -state online` (T2) |
| `qos statistics volume latency show` | `qos statistics workload latency show` / `qos statistics performance show` |
| `vserver nfs connected-clients show` | `nfs connected-clients show -vserver S [-volume V]`. **Lists only clients with traffic in the last 48h.** Idle mounts are invisible (p1393). |
| `security anti-ransomware volume attack-reports` | `security anti-ransomware volume attack generate-report -vserver S -volume V -dest-path S:/path` |

## By area (read commands first)
- **Cluster / nodes:**
  - read: `cluster show`, `version`, `cluster image show`, `system node image show` *(adv)*, `system node upgrade-revert show`, `system health status show`, `system health subsystem show`, `system health alert show`, `event log show`
  - changes: `system node reboot`, `system node halt` (T3, vendor/runbook)
- **Upgrade:**
  - read: `cluster image package show-repository`, `cluster image validate -version V [-show-validation-details true]`, `system node image show-update-progress`, `system node firmware bootmedia show`
  - changes: `cluster image package get -url U` (T1), `cluster image update` (T3)
- **HA:**
  - read: `storage failover show`, `storage failover show-giveback`
  - changes: `storage failover takeover`, `storage failover giveback`, `storage failover modify` (T3)
- **Local tiers:**
  - read: `storage aggregate show`, `show-space`, `show-status`, `show-spare-disks`, `storage aggregate relocation show`, `storage aggregate object-store show` (FabricPool)
  - changes: `storage aggregate create|add-disks|modify|offline|delete` (T2/T3), `storage aggregate relocation start` (T3)
- **Volumes:**
  - read: `volume show -fields ...`, `volume show-space`, `volume show-footprint`, `volume move show`, `volume clone show`, `volume efficiency show`
  - changes: `volume size`, `volume modify` (T2), `volume move start` / `trigger-cutover` (T2, heavy I/O), `volume clone create` / `split start` (T1/T2), `volume unmount` → `volume offline` → `volume delete` (T3)
- **Recovery queue** (*adv*):
  - `volume recovery-queue show`
  - `volume recovery-queue recover` (T2)
  - `volume recovery-queue modify` (retention)
  - `volume recovery-queue purge` / `purge-all` (T3, irreversible, MAV-protectable)
  - **Deleting the owning SVM empties the queue** (p718)
- **Snapshots:**
  - read: `volume snapshot show`, `volume snapshot policy show`, `volume snapshot autodelete show`, `volume snapshot compute-reclaimable` *(adv)*
  - changes: `volume snapshot create` (T1), `volume snapshot policy create|add-schedule|modify-schedule|modify` (T2), `volume snapshot autodelete modify` (T2), `volume snapshot restore-file -path P [-restore-path D]` (T2, single file/LUN), `volume snapshot partial-restore-file` (T2), `volume snapshot restore` (T3, whole volume), `volume snapshot delete` (T3), `volume snapshot modify-snaplock-expiry-time` (T3, locked snapshots)
- **SAN:**
  - read: `lun show`, `lun mapping show`, `igroup show`, `iscsi initiator show -fields igroup,initiator-name,tpgroup`, `fcp initiator show -fields igroup,wwpn,lif`
  - changes: `lun mapping create` (T1), `igroup add` (T1), `igroup remove` (T3), `lun mapping delete` (T3), `lun delete` (T3, MAV-protectable)
- **NAS:**
  - read: `vserver export-policy show`, `vserver export-policy rule show`, `vserver export-policy check-access`, `vserver cifs share show`, `vserver cifs share access-control show`, `nfs connected-clients show`
  - changes: `vserver export-policy rule create|modify|setindex` (T2), `vserver cifs share access-control create|delete` (T2/T3), `vserver export-policy cache flush` (T2)
- **Networking:**
  - read: `network interface show [-is-home false]`, `network interface failover-groups show`, `network interface service-policy show`, `network interface check cluster-connectivity`, `network port show`
  - changes: `network interface revert` (T2: back to home port), `network interface migrate` / `migrate-all` (T3), `network interface modify|delete` (T3), `network interface failover-groups create|modify` (T2)
- **Peering:**
  - read: `cluster peer show`, `cluster peer health show`, `vserver peer show`, `vserver peer permission show`
  - changes: `cluster peer create` / `vserver peer create|accept` (T1), `cluster peer delete` / `vserver peer delete` (T3, breaks all SnapMirror over it)
- **SnapMirror:**
  - read: `snapmirror show [-expand]`, `snapmirror list-destinations`, `snapmirror policy show`, `snapmirror mediator show`, `snapmirror failover show`
  - changes:
    - `snapmirror create|initialize|protect` (T1)
    - `snapmirror update` (T1)
    - `snapmirror policy create|add-rule` (T2)
    - `snapmirror quiesce` / `resume` (T2)
    - `snapmirror break` (T3, **run from the destination**)
    - `snapmirror resync [-quick-resync true|false]` (T3, run from the destination; quick-resync can lose storage-efficiency savings)
    - `snapmirror restore` (T3)
    - `snapmirror delete` + `snapmirror release` (T3)
    - `snapmirror failover start` (active sync, T3 runbook)
    - `snapmirror mediator add|remove` (T3)
- **MetroCluster** (read): `metrocluster show`, `metrocluster check run`, `metrocluster operation show`, `metrocluster node show`. `metrocluster switchover|heal|switchback` is the T3 DR runbook only.
- **Security:** see ontap-security-and-ransomware.md. Also:
  - `security key-manager show|key query|external show-status` (read)
  - `security key-manager onboard sync|update-passphrase` (T3)
  - `volume encryption conversion|rekey|secure-purge start` (T2/T3)
- **AutoSupport:**
  - read: `system node autosupport show`, `system node autosupport history show`, `system node autosupport check show`
  - changes: `system node autosupport invoke` (T1; tell the user, because it sends data to NetApp)
