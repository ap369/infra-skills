# Terraform reference: workflow, state, lifecycle, changes by tier

> **Command verification status:** CLI forms are checked against terraform-command-catalog.md (HashiCorp CLI reference, Terraform 1.17); those forms are `[doc]`. Language facts (`lifecycle`, `moved`, `removed`, `import` blocks, state, locking) are from developer.hashicorp.com (web-unified-docs, v1.17.x), retrieved 2026-10-25. Provider resources and arguments are `[unverified]` until checked in that provider's documentation for the locked version.

## The safe workflow
```
terraform fmt -check -recursive                                  [doc]
terraform init                                                   [doc]   (uses .terraform.lock.hcl)
terraform validate                                               [doc]
terraform plan -out=<ticket>.tfplan                              [doc]
terraform show <ticket>.tfplan                                   [doc]   (human review)
terraform show -json <ticket>.tfplan > <ticket>.plan.json        [doc]   (machine checks)
terraform apply <ticket>.tfplan                                  [doc]   (the reviewed plan, nothing else)
```
- A saved plan file applies the reviewed operations, and **`terraform apply <file>` runs them without prompting** (HashiCorp: "performs the operations in the saved plan without prompting you for confirmation"). So the human approval happens on the `terraform show` output of that file, before the apply step. Plan files contain sensitive values: store them like state. If anything changed since the review, plan again and re-approve.
- In CI: `plan -detailed-exitcode` gives 0 = no changes, 1 = error, 2 = changes present. Fail the pipeline on unexpected 2s for "no-op" runs.
- **`-auto-approve` skips confirmation.** HashiCorp warns to use it only when nobody can change infrastructure outside the Terraform workflow. Never combine it with a fresh, unreviewed plan in production.
- `-target` is for "exceptional circumstances only" (HashiCorp). A targeted apply leaves the rest of the configuration unreconciled.

## Reading a plan (what to put in the change plan)
- The summary line: N to add, N to change, **N to destroy**. Any destroy, or "must be replaced" (`-/+` / `+/-`), of a **stateful** resource (volumes, buckets, databases, file systems, DNS zones, anything holding data) makes the change **T3**.
- `create_before_destroy` vs. the default destroy-then-create order: replacement can cause an outage window.
- Changes you didn't expect = drift or someone else's change. Stop and investigate before applying.

## State
- State maps configuration to real objects and **contains secrets** (passwords, keys, connection strings) in plain text. Protect the backend (encryption, access control); never commit state; never paste it into chat.
- HashiCorp recommends a remote backend (or HCP Terraform) with locking; "avoid storing your state in a version control system or other storage solution that does not support Terraform state locking".
- **Locking:** "Terraform will lock your state for all operations that could write state." If locking fails, Terraform does not continue.
- **`force-unlock`:** "Be very careful with this command. If you unlock the state when someone else is holding the lock it could cause multiple writers." Use it only for your own lock after automatic unlock failed: check CI runs and colleagues first (T3).
- **`state rm`** "removes the binding to an existing remote object without first destroying it". The object keeps running, unmanaged. HashiCorp recommends a `removed` block with `lifecycle { destroy = false }` instead, because it can be previewed in a plan.
- **`state mv`** or, better, a **`moved` block** (reviewable in code): renames without destroying.
- Before any state surgery: `terraform state pull > <ticket>-state-backup.tfstate` `[doc]` (store it securely: it has secrets).

## Lifecycle rules (language docs)
- **`prevent_destroy = true`:** plans that would destroy the object fail. **It does not protect against removing the resource block**: if the configuration is removed, Terraform destroys the object ("This rule doesn't prevent Terraform from destroying a resource if you remove its configuration"). Review deletions of resource blocks as T3.
- **`removed` block:** by default "Terraform removes the resource from state and destroys the actual resource". Set `lifecycle { destroy = false }` to only forget it. Documented form (HashiCorp *Remove a resource from state*): replace the `resource` block with
  ```hcl
  removed {
    from = <resource address, without instance keys>
    lifecycle {
      destroy = false
    }
  }
  ```
- **`ignore_changes`:** for attributes managed outside Terraform. Overuse hides drift.
- **`import` block:** brings an existing object under management; the plan shows what Terraform would change on import. Check that the plan has **no** changes to imported objects before applying.

## Drift and incidents
- `terraform plan -refresh-only` shows what changed outside Terraform without proposing to revert it. Use it after incidents (manual fixes) to update state deliberately, or update the code to match.
- A normal `apply` after a manual fix will revert the fix: reconcile code first.

## Storage-system providers (Terraform Registry, checked 2026-10-25)
| Provider | Registry | Version | Tier |
|---|---|---|---|
| NetApp ONTAP | `NetApp/netapp-ontap` | 2.7.1 | partner |
| Dell PowerMax | `dell/powermax` | 1.0.4 | partner |
| Dell ObjectScale | `dell/objectscale` | 1.1.1 | partner |
| Pure Storage | no official provider found (only community `devans10/flash`, last release 2020: don't use in production) | — | — |
Pin every provider in `required_providers` and commit `.terraform.lock.hcl`. A destroy or replace of a volume, LUN, file system, bucket or masking object through these providers is **T3** and must also pass the matching storage skill's checks (host access, snapshots, replication).

## Changes by tier
| Tier | Operation | Form | Rollback |
|---|---|---|---|
| T1 | Apply an add-only plan | `terraform apply <file>.tfplan` | destroy the new objects via code revert |
| T2 | Apply in-place updates | same | revert commit, plan, apply |
| T2 | Import | `import` block or `terraform import <addr> <id>`, then a no-change plan | `removed` block with `destroy = false` |
| T2 | Rename/move | `moved` block (preferred) or `terraform state mv <from> <to>` | reverse move |
| T3 | Destroy / replace stateful | reviewed plan file only, data backed up first | restore from backup |
| T3 | `terraform destroy` | never for production stacks without a decommission plan | none |
| T3 | Forget a resource | `removed` + `destroy = false`, or `terraform state rm <addr>` | `import` |
| T3 | Unlock | `terraform force-unlock <LOCK_ID>` after proving the lock is yours | n/a |
