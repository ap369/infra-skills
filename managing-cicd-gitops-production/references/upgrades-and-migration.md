# Upgrades and migration: Argo CD, Flux, CI runners

> **Command verification status:** facts from Argo CD *Upgrading* overview (docs, 3.7 tree) and Flux docs; install/upgrade manifests and Helm values are `[unverified]` here: use the project's upgrade guide for the exact version.

## Argo CD
- Patch releases: no breaking changes. Minor releases may need workarounds: **read the upgrade notes for every minor you cross** (1.3 → 1.5 means both 1.3→1.4 and 1.4→1.5). Majors are incompatible changes.
- Before: export Applications/AppProjects/settings (Git should already hold them), note the current version (`argocd version` `[doc]`), check Kubernetes version support for the target Argo CD.
- During the upgrade, consider disabling auto-sync on critical apps so a controller restart can't trigger unexpected syncs; re-enable after verifying.

## Flux
- `flux check --pre` `[doc]` checks prerequisites. Upgrade the CLI and controllers together; read the release notes for API version graduations (CRD `apiVersion` changes in your manifests).
- If Flux is bootstrapped, upgrades go through the bootstrap repository (a reviewed commit).

## CI runners and platforms
- Upgrade runners in a pool one at a time; keep the old image available to roll back.
- Workflow syntax changes (new keywords, deprecated commands) are checked in the platform's changelog before the upgrade.

## Migration (CI system or GitOps tool)
Run old and new side by side on non-production first, migrate one application at a time, disable sync/deploy in the old tool for each migrated app (never two controllers managing the same objects), keep the old configuration until the quarantine ends.
