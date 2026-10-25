# Terraform and provider upgrades, migration

> **Command verification status:** forms are `[doc]` per terraform-command-catalog.md. Version-specific upgrade notes come from HashiCorp's upgrade guides and each provider's CHANGELOG: read them for every version you cross (they're not reproduced here).

## Terraform CLI upgrades
- Pin `required_version`. Upgrade in a branch: `terraform init`, `validate`, `plan` against every environment, and expect **no changes** from the upgrade alone.
- HashiCorp: "new Terraform versions are generally backward compatible with state snapshots produced by earlier versions. However, the state format is subject to change". The reverse isn't promised: after a newer version writes the state, don't assume older versions can still use it. Upgrade every pipeline and admin workstation for that state together, and never parse state JSON in your own tools (use `show -json` / `output -json`).
- Back up state first: `terraform state pull > <ticket>-state-backup.tfstate` `[doc]` (secure storage).

## Provider upgrades
- One provider at a time, one major version at a time. `terraform init -upgrade` `[doc]` updates the lock file within the constraints; commit the new `.terraform.lock.hcl`.
- Read the provider CHANGELOG / upgrade guide: renamed attributes, changed defaults and new "forces replacement" behaviour show up as plan changes.
- `terraform providers lock -platform=<os_arch>` `[doc]` for every platform your CI and admins use.
- A plan with replacements after a provider upgrade is a **stop sign** (T3), especially for storage-provider resources.

## Backend migration (T3)
`terraform init -migrate-state` `[doc]` copies state to the new backend (`-reconfigure` ignores existing state: wrong flag for a migration). Lock out other runs, back up state, migrate, then verify `state list` matches and `plan` shows no changes.

## Refactoring and splitting state
Use `moved` blocks for renames and module moves; to split a state, `removed` (destroy = false) in the old root plus `import` blocks in the new one, each with a no-change plan. Never edit state JSON by hand.
