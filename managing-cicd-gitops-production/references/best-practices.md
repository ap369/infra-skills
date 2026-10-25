# Best practices: configuration audit (CI/CD and GitOps)

> **Command verification status:** reads use forms from the catalogs (`[doc]`). Practices come from GitHub Docs *Secure use reference* (Actions), Argo CD docs (*Automated Sync Policy*, *App Deletion*), Flux kustomize-controller docs, retrieved 2026-10-25. Site standards override them.

Every check is read-only (T0). Report: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## Pipelines
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| C1 | Third-party actions/plugins pinned to full commit SHA (or lockfile) | Supply-chain takeover | workflow files | T2 |
| C2 | CI token permissions set to the minimum per workflow/job | Blast radius | workflow `permissions` / CI settings | T2 |
| C3 | Cloud access via OIDC, no long-lived cloud keys in CI secrets | Key theft | secrets list (names only) | T2 |
| C4 | No `pull_request_target`/`workflow_run` workflows that check out untrusted PR code | Repo takeover | workflow triggers | T2 |
| C5 | Untrusted input passed via env vars, never inlined in scripts | Script injection | workflow scripts | T2 |
| C6 | Production deploys use a protected environment with required reviewers; branch protection on deploy branches | Unreviewed prod changes | repo settings | T2 |
| C7 | Ephemeral runners; self-hosted runners not shared across trust levels | Persistent compromise | runner config | T3 |
| C8 | Artifacts built once, promoted by digest across environments; SBOM/signature produced | Reproducibility, provenance | pipeline | T2 |
| C9 | Secrets rotated after any exposure in logs; secret scanning enabled | Leaks | settings | T2 |

## GitOps
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| G1 | Auto-prune on production apps only where a bad commit deleting objects is acceptable, otherwise prune by approved manual sync | Accidental deletion | `argocd app get` sync policy; Kustomization `spec.prune` | T2 |
| G2 | Argo CD apps with stateful workloads: deletion behaviour known (cascade/finalizer) and documented | Data loss on app delete | Application finalizers | T2 |
| G3 | Flux Kustomizations with stateful workloads: `deletionPolicy` set deliberately | Data loss on Kustomization delete | spec | T2 |
| G4 | Git repo is the single source: drift alerts on OutOfSync/Not Ready, manual cluster edits forbidden | Drift | app/kustomization status | T2 |
| G5 | Controller access least privilege (projects/RBAC per team, no cluster-admin for tenant apps) | Blast radius | AppProjects, RBAC | T2 |
| G6 | Sync windows / freeze periods configured for change freezes | Freeze compliance | Argo CD sync windows | T2 |
| G7 | Argo CD / Flux on supported versions; upgrade notes read per minor | Security, compatibility | `argocd version`, `flux version` | T3 |
