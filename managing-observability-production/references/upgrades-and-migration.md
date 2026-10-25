# Upgrades and migration: Prometheus, Alertmanager, Icinga 2, Dynatrace

> **Command verification status:** forms from the catalogs. Version-specific steps come from each project's upgrade notes: Prometheus `docs/migration.md` (2.x → 3.x), Icinga 2 `doc/16-upgrading-icinga-2.md`, Dynatrace release notes. Package commands are `[unverified]` here.

## Prometheus / Alertmanager
- Read the release notes for every version crossed. Prometheus ships a migration guide for the 2.x → 3.x major (`docs/migration.md` in the release): flag and config changes, UI changes.
- Validate the existing config with the **new** `promtool check config` / `check rules` before switching binaries.
- HA pairs: upgrade one instance, compare rule evaluation and alerts with the other, then the second. Keep the previous binary for rollback; TSDB format changes may prevent downgrades: read the notes and snapshot first (`/api/v1/admin/tsdb/snapshot` if the admin API is enabled).
- Alertmanager cluster: one member at a time; silences replicate across members.

## Icinga 2
- Follow `16-upgrading-icinga-2.md` for each version crossed. Upgrade the config master first, then satellites, then agents (the docs' distributed-monitoring guidance); validate with `icinga2 daemon -C` after each package upgrade.
- Back up `/etc/icinga2`, `/var/lib/icinga2` (API state, certificates) before upgrading.

## Dynatrace
- SaaS upgrades are vendor-managed; ActiveGates and OneAgents follow the environment's update settings. Plan OneAgent updates per host group (they can restart monitored processes' instrumentation).
- Monaco: pin the version in CI; run `monaco deploy --dry-run` with the new version before switching.

## Migration (tool to tool, e.g. Icinga → Prometheus or Dynatrace)
Run both in parallel, compare coverage (every check/alert has an equivalent with the same severity and receiver), switch paging per service, keep the old system read-only until the quarantine ends. Never leave a gap where neither system pages.
