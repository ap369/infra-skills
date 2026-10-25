# Terraform health checks and incident triage

> **Command verification status:** forms are `[doc]` per terraform-command-catalog.md (Terraform 1.17). Facts from HashiCorp docs as cited in terraform.md.

## Health check (T0)
| # | Check | Read | Warning | Critical |
|---|---|---|---|---|
| 1 | Drift | `terraform plan -detailed-exitcode` (exit 2 = changes) or `plan -refresh-only` | unexpected changes | unexpected destroys |
| 2 | Versions | `terraform version`, `terraform providers` | providers behind | unsupported Terraform/provider |
| 3 | Lock file | `.terraform.lock.hcl` committed and current | missing platforms | missing |
| 4 | State size/health | `terraform state list` count; plan duration | slow plans | errors reading state |

## Playbooks
### "Error acquiring the state lock"
1. Read the lock info in the error (ID, who, when, operation).
2. Find the holder: a running CI job, a colleague, a crashed run.
3. If a run is active, wait. If the holder crashed, **the holder** (or the pipeline owner) runs `terraform force-unlock <LOCK_ID>` as an approved T3 step. Never unlock someone else's live lock.

### Apply failed halfway
Terraform records what it completed. Don't re-run blindly: `terraform plan` again, read what's left, check the provider error (quota, permission, API limit, dependency). Fix the cause, then apply a new reviewed plan.

### Plan wants to destroy/replace something important
Stop. Common causes: a renamed resource (use `moved`), a changed immutable attribute (forces replacement), a provider upgrade changing defaults, a removed resource block, drift. Find the cause in the plan diff ("forces replacement" lines) before anything else.

### Drift after an incident
`plan -refresh-only` to see it. Decide with the owner: update code to keep the fix, or apply to revert it. Never let a scheduled apply revert an emergency fix silently.

### Provider authentication errors
Expired credentials or wrong identity in CI. Don't switch to personal admin credentials to "make it work".

## Communication
Use incident-comms.md. Name the root module / workspace and the environment in every update.
