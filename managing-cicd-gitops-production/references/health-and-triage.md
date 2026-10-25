# CI/CD and GitOps health checks and triage

> **Command verification status:** Argo CD / Flux forms are `[doc]` per the catalogs (Argo CD 3.7.0, Flux 2.9.6).

## Health check (T0)
| # | Check | Read | Warning | Critical |
|---|---|---|---|---|
| 1 | Argo CD apps | `argocd app list` (SYNC STATUS, HEALTH) | OutOfSync | Degraded / Missing on production |
| 2 | Flux | `flux --context <ctx> get all --all-namespaces` | suspended unexpectedly | Ready=False on production |
| 3 | Controllers | `flux --context <ctx> check`; Argo CD pods in its namespace (`kubectl`) | restarts | controller down |
| 4 | Pipelines | CI dashboard / API | flaky jobs | deploy pipeline blocked |

## Playbooks
### Argo CD app OutOfSync / Degraded
1. `argocd app get <app> --refresh` and `argocd app diff <app>` `[doc]`: what differs, which resource is unhealthy.
2. Drift from a manual edit + selfHeal → it'll be reverted; decide whether Git or the edit is right.
3. Degraded after a deploy → Git revert (or `app rollback` when auto-sync is off; "Rollback cannot be performed against an application with automated sync enabled").

### Flux Kustomization not ready
`flux events -n <ns>`, `flux logs -n flux-system`, `flux get kustomizations` for the error (build failure, validation, dependency not ready, source fetch failure). Fix in Git, then `flux reconcile kustomization <name> -n <ns> --with-source` (T2).

### Stuck deletion (finalizers)
An Application or Kustomization stuck deleting is usually waiting to delete its resources. Removing the finalizer orphans or skips cleanup: T3, decide with the owner.

### Deploy pipeline failing
Read the failing step's log. Don't re-run blindly (it may pick a different commit or artifact). Never bypass required reviewers or branch protection to "unblock".

### Leaked secret in CI logs
Treat as compromised: rotate at the source (T2/T3 depending on blast radius), remove the log if the platform allows, find how it leaked (echo, debug mode, encoding).
