# Upgrade checklist (OS / code / firmware)

Upgrades are T3. They usually run as a vendor-led or vendor-orchestrated rolling procedure. Claude prepares and checks the readiness evidence, drafts the change plan, and watches health between phases. It doesn't improvise steps outside the vendor procedure. Platform specifics are in references/upgrades-and-migration.md.

## 1. Readiness (all T0 reads, recorded in the plan with timestamps)
- [ ] **Target and path:** current version → target version, and the vendor's supported upgrade path (some need intermediate hops).
- [ ] **Why this version:** vendor recommended / target code, the fixes needed, the known issues read (release notes), and the end-of-support dates.
- [ ] **Compatibility:**
  - host OS, HBA/driver and multipath versions against the vendor's interoperability matrix
  - replication peers (both ends must support the version pair)
  - management tools, plugins and backup software
- [ ] **Health gate:**
  - no open critical alerts
  - no failed or degraded components
  - no rebuild, resync or rebalancing in progress
  - capacity below the vendor's upgrade threshold
- [ ] **Redundancy gate:** every host has paths through every controller/node that will reboot. For erasure-coded or object systems, the margin math allows one node offline plus one unplanned failure.
- [ ] **Vendor pre-check tool** run and clean (the upgrade-readiness or health-check report), and the vendor case opened if the procedure is vendor-led.
- [ ] **Backups and config:** a config backup / export taken, recent good snapshots or backups of critical data, the license and support contract valid.
- [ ] **Window and freeze:** an agreed window with time for rollback, no freeze conflict, stakeholders notified (references/incident-comms.md P3 template), and the app teams aware of path failovers.

## 2. Plan structure
1. Upgrade management components first if the vendor requires it (manager, plugins).
2. For replicated pairs, follow the vendor's order. **DR / destination first** is common, but confirm it for the platform.
3. Go one node, controller or device per phase. After each: health back to full, paths restored, rebuild/resync caught up, and no new alerts before the next phase.
4. Abort criteria, stated up front: a node that doesn't return, a path that doesn't recover, a new critical alert, or latency over the agreed threshold for more than N minutes.
5. Rollback or back-out: what the vendor allows (many upgrades can't be rolled back after commit). Say this explicitly in the plan.

## 3. Post-upgrade
- Version confirmed on every component. No mixed versions left unintentionally.
- Paths, replication, snapshots/schedules and monitoring verified.
- Release-note follow-ups done, such as new defaults or features to enable. Re-run references/best-practices.md for the items affected.
