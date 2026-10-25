# Best practices: configuration audit (Terraform)

> **Command verification status:** reads use forms from terraform-command-catalog.md (`[doc]`). Practices come from developer.hashicorp.com (state, locking, `lifecycle`, `removed`, `apply`/`plan` references, v1.17.x), retrieved 2026-10-25. Site standards override them.

Every check is read-only (T0). Report: **# | Practice | Current value | Status (OK / GAP / N/A) | Risk | Fix (tier)**, then a prioritized summary.

## State and backends
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| T1 | Remote backend with **locking** for every shared/production root module; never local or VCS state | Corruption, lost state | `terraform` block / backend config | T3 (backend migration) |
| T2 | Backend encrypted, access restricted to the pipeline and admins, versioning/backups on the state store | State holds secrets; recovery | backend storage settings | T2 |
| T3 | One state per environment and blast-radius unit (no giant all-in-one state) | Smaller blast radius, faster plans | repo layout | T3 (state split) |
| T4 | No `force-unlock` without a recorded reason | Concurrent writers | CI logs / audit | process |

## Change workflow
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| T5 | All production applies from CI using a **saved plan** reviewed by a human; no laptop applies | Reproducible, audited | pipeline definition | T2 |
| T6 | No `-auto-approve` on a plan nobody reviewed | Unreviewed destroys | pipeline | T2 |
| T7 | Plans with destroy/replace of stateful resources require an extra approval | Data loss | pipeline policy (e.g. a policy check on `show -json`) | T2 |
| T8 | Scheduled drift detection (`plan -detailed-exitcode` or `-refresh-only`) with alerting | Silent drift | scheduler | T2 |
| T9 | `-target` not used routinely | Partial applies, hidden drift | pipeline/scripts | T2 |

## Code
| # | Practice | Why | Check | Fix tier |
|---|---|---|---|---|
| T10 | Terraform version pinned (`required_version`) and providers pinned (`required_providers`) with `.terraform.lock.hcl` committed | Unexpected upgrades | code | T2 |
| T11 | Modules pinned to versions/commit refs, not branches | Supply chain, surprise changes | module sources | T2 |
| T12 | `prevent_destroy` on critical stateful resources, **and** review rules for removing resource blocks (it doesn't protect against that) | Accidental destroys | code + review policy | T2 |
| T13 | Refactors use `moved` / `removed` blocks, not ad-hoc `state` commands | Reviewable, previewable | code history | T2 |
| T14 | Secrets come from a secret manager or ephemeral values, not variables in Git; outputs marked `sensitive` | Leaks | code | T2 |
| T15 | `fmt -check` and `validate` in CI; a security/policy scanner for misconfigurations | Quality | pipeline | T2 |
| T16 | Storage resources (volumes, LUNs, buckets) managed by Terraform are tagged and cross-checked with the storage skills before destroy | Data loss on arrays | code, storage skill | process |
