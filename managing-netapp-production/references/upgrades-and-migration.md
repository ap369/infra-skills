# Upgrades and migration: NetApp

Use with references/upgrade-checklist.md (generic gates) and references/change-gate.md. Confirm against NetApp's upgrade documentation, Digital Advisor's Upgrade Advisor and the Interoperability Matrix Tool (IMT) for your release.

## ONTAP upgrades (ANDU)
- **How:**
  - automated non-disruptive upgrade: `cluster image package get`, then `cluster image validate`, then `cluster image update`, or through System Manager
  - **MetroCluster** and **SnapMirror active sync** clusters have their own procedures
  - firmware for disks, shelves and SP/BMC is usually bundled
- **Extra readiness checks:**
  - Digital Advisor **Upgrade Advisor** plan for the cluster, and `cluster image validate` clean
  - IMT: host OS, HBAs, multipath, host utilities, and the SnapCenter/backup software versions
  - **SnapMirror interoperability** is **bidirectional and matrix-based** (docs p226: "Compatible ONTAP versions for SnapMirror relationships"). There's no fixed source-first or destination-first rule: **every intermediate version pair** during the rolling upgrade of both clusters must be in the matrix. **SVM-DR needs the same version on both sides** for failover and failback (p2713). With FlexGroup advanced capacity balancing (9.16.1+), you can't replicate to clusters older than 9.16.1.
  - `storage failover show`: takeover possible on every HA pair. LIFs home. Failover groups span both nodes (best-practices.md N15).
  - no `volume move`, SnapMirror baseline or aggregate reconstruction running
- **Watch between nodes:**
  - giveback complete
  - LIFs back home
  - SAN paths restored
  - no new EMS errors
  - latency normal
- **StorageGRID:** upgrade from the Grid Manager (primary admin node first, then rolling). Check ILM backlog and node health first.

## What the ONTAP documentation adds (PDF 2026-10-08, page refs)
- **Target choice (p162):** NetApp recommends the latest patch of the latest numbered release your hardware supports (check Hardware Universe), or at least the *minimum recommended release*. If the hardware can't run the target, the path is add nodes → migrate data → remove old nodes → upgrade.
- **Planning tools (p159–163):**
  - **Upgrade Advisor** (Digital Advisor, needs AutoSupport) or **Upgrade Health Checker** generates an upgrade plan with blockers.
  - **Config Advisor** catches common configuration errors.
  - Resolve the Digital Advisor risks in the SW/HW config-change and HW-replacement categories first.
- **Automated pre-checks:** `cluster image validate -version V -show-validation-details true` runs about 75 checks. You can run it **weeks before** the window. Fix every error, and fix warnings as best practice. For a direct multi-hop upgrade, load and validate only the **target** image. MetroCluster: validate cluster A, then cluster B (p150–152).
- **Manual preparation (p161):**
  - read the release notes' *Upgrade cautions* and *Known problems*
  - confirm hardware, switch and SAN support (IMT)
  - verify LIF failover policies and groups, and SVM routing
  - handle special configurations (MetroCluster, SnapMirror, FIPS with SSH public keys, and so on)
  - reboot the SP/BMC before the upgrade
- **Paths (p163):** direct, direct multi-hop, or multi-stage. ANDU is recommended whenever possible.
- **Methods (p249–250):** System Manager or CLI. **Rolling upgrade** (node by node, partner takeover) is the default under 8 nodes. **Batch upgrade** applies from 8 nodes up. Both are non-disruptive. A 4-node MetroCluster on 9.3+ should use System Manager automated upgrade.
- **Duration (p159):** about 30 min of prep + **about 60 min per HA pair** (longer with external KMIP key managers) + about 30 min of post-checks.
- **Firmware:** from 9.17.1, ANDU keeps BIOS/LOADER firmware that was pre-staged and is newer (`system node firmware bootmedia show`, p324).
- **Post-upgrade (p302):**
  - `version` on every node (the cluster version is the **lowest** node version)
  - cluster and storage health
  - **revert LIFs not on their home port** (`network interface revert`)
  - MetroCluster FC: automatic unplanned switchover enabled
  - **update the Disk Qualification Package (DQP)**, which the upgrade doesn't do
- **Revert:** see ontap-versions-and-defaults.md. It's disruptive, one release at a time, and needs NetApp support for production.

## Migration / tech refresh
Options, from least disruptive to most:
1. **Within a cluster:** `volume move` (non-disruptive, to new aggregates or new nodes added to the cluster), then remove old nodes (`cluster unjoin`, NetApp procedure). This is the classic head swap.
2. **Cluster to cluster:** SnapMirror, SVM-DR, or **SVM migrate** (9.10.1+, run from the **destination**):
   - prechecks: `vserver migrate start -vserver S -source-cluster C -check-only true`
   - start: `vserver migrate start ...`
   - monitor: `vserver migrate show` / `show-volume`
   - control: `pause`, `resume`, `abort`
   - automatic client cutover and source cleanup by default (p648–652)
   
   For SnapMirror cutover:
   1. final update
   2. quiesce / break **on the destination**
   3. redirect clients (DNS, LIFs or remount)
   4. keep the source read-only until sign-off
3. **From third-party NAS/SAN:** XCP (NFS/SMB) or Foreign LUN Import (FLI, FC; **iSCSI from 9.19.1**), plus host-based tools.
4. **To StorageGRID / cloud tiers:** FabricPool policies (T2/T3: tiering changes performance and cost).

**Checklist for any migration:**
- inventory: SVMs, volumes, junctions, export policies, shares/ACLs, LUN maps, igroups, snapshot policies, SnapMirror
- the target sized with efficiency assumptions **stated**
- cutover per application
- rollback: the source is untouched until sign-off
- decommission the source with the staged pattern in ontap.md
