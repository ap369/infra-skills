# CI/CD and GitOps reference: pipelines, Argo CD, Flux, changes by tier

> **Command verification status:** Argo CD and Flux CLI forms are checked against argocd-command-catalog.md (Argo CD 3.7.0 command reference) and flux-command-catalog.md (Flux 2.9.6 CLI source); those forms are `[doc]`. Facts are from argo-cd.readthedocs.io sources (*Automated Sync Policy*, *App Deletion*, *Upgrading*), fluxcd kustomize-controller *Kustomization* spec, and GitHub Docs *Secure use reference* for Actions, retrieved 2026-10-25. Pipeline YAML syntax for GitHub Actions / GitLab CI / Jenkins isn't catalogued: keywords are `[unverified]` until checked in that product's documentation.

## Pipeline security (GitHub Docs, Secure use; principles apply to any CI)
- **Pin third-party actions to a full-length commit SHA** (or use workflow dependency lockfiles where adopted). A tag can be moved to malicious code.
- **Least privilege for the CI token:** grant `GITHUB_TOKEN` (or the equivalent) the minimum permissions; set them per workflow/job.
- **OIDC to the cloud** instead of long-lived cloud keys stored as secrets.
- **Script injection:** untrusted input (`github.event.pull_request.title`, branch names…) must not be interpolated into inline scripts; pass it through an environment variable or an action argument.
- **`pull_request_target` and `workflow_run` with a checkout of untrusted PR code are dangerous**: these workflows are privileged and "may have repository write access and access to referenced secrets"; they can be exploited "to take over a repository".
- Self-hosted runners for public repositories, or shared between trust levels, can be persistently compromised: prefer ephemeral runners.
- Production deployments go through a protected environment with required reviewers; branch protection on the deploy branch; nobody merges their own production change without review.
- Secrets never echoed; masked values still leak through encodings or files: treat any secret that hit a log as compromised and rotate it.

## Argo CD
- **Automated sync** (`spec.syncPolicy.automated`): `prune` deletes resources removed from Git, `selfHeal` reverts manual changes, `allowEmpty` allows syncing to an empty set. Setting `automated.enabled` to null is treated as enabled. Prune + selfHeal on production means **Git is the only lever**; a bad commit propagates by itself.
- **Deletion:** "A cascade delete deletes both the app and its resources". `argocd app delete <app>` with no flag **cascades**; `--cascade=false` deletes only the Application. Deleting an Application object with `kubectl` cascades if the `resources-finalizer.argocd.argoproj.io` finalizer is set.
- **Upgrades:** patch releases have no breaking changes; minor releases may need workarounds, so read the upgrading notes for **every** minor you cross (e.g. 1.3 → 1.5 means both the 1.3→1.4 and 1.4→1.5 notes); majors introduce incompatible changes.

Reads (T0):
```
argocd app list                                  [doc]
argocd app get <app> --refresh                   [doc]
argocd app diff <app>                            [doc]
argocd app history <app>                         [doc]
argocd app manifests <app>                       [doc]
```

## Flux
- **`.spec.prune`** (required): objects previously applied but missing from the current source revision "are removed from the cluster automatically".
- **`.spec.suspend`**: stops applying new revisions and pauses drift detection/correction. Resume by setting it back to false or `flux resume`.
- **`.spec.deletionPolicy`**: default `MirrorPrune` deletes the managed resources when the Kustomization is deleted if `prune: true` (orphans them if false). Read it before any `flux delete kustomization`.

Reads (T0):
```
flux --context <ctx> get all --all-namespaces             [doc]
flux --context <ctx> get kustomizations --all-namespaces  [doc]
flux --context <ctx> diff kustomization <name> --path <dir>   [doc]
flux --context <ctx> events -n <ns>                      [doc]
flux --context <ctx> logs -n flux-system                 [doc]
flux --context <ctx> tree kustomization <name> -n <ns>   [doc]
```

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T2 | Deploy via Git | reviewed PR merged to the watched branch | `git revert` + sync |
| T2 | Manual sync (no prune) | `argocd app sync <app>` after `app diff`; `--dry-run` first | `argocd app rollback <app> <history-id>` (only when auto-sync is off) |
| T2 | Roll back | Git revert (preferred), or `argocd app rollback <app> <id>` | re-sync to Git |
| T2 | Pause GitOps for an incident | `flux suspend kustomization <name> -n <ns>`; Argo: `argocd app set <app> --sync-policy none` | `flux resume ...`; restore the sync policy |
| T2 | Force a Flux reconcile | `flux reconcile kustomization <name> -n <ns> --with-source` | n/a |
| T3 | Sync with prune | `argocd app sync <app> --prune` only with the list of objects to be pruned approved (from `app diff`) | recreate from Git; **data in deleted PVCs is gone** |
| T3 | Delete an Argo CD app | `argocd app delete <app> --cascade=false` to keep resources; cascade only for an approved decommission | re-create the Application |
| T3 | Delete a Flux Kustomization | read `prune` and `deletionPolicy` first; `flux delete kustomization <name> -n <ns>` | re-create from Git |

`argocd app sync` / `delete` accept `--selector`/label selectors: never target more than the named app in production plans.
