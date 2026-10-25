---
name: managing-terraform-production
description: Use when planning, reviewing, applying, or troubleshooting Terraform for production infrastructure - terraform plan, apply, destroy, state, remote backends, state locks, force-unlock, import, state mv or rm, drift, refresh-only, workspaces, modules, provider and version upgrades, prevent_destroy, storage providers (NetApp ONTAP, Dell PowerMax, Dell ObjectScale), CI pipelines for Terraform, best practices, configuration audit.
---

# Managing Terraform in Production

## Overview
Reading is free; every change is a **change plan** (references/change-gate.md), executed only after the user approves *that plan*. Violating the letter of the gate violates its spirit. **No change is 100% safe:** end every plan with the safety notice. **Never invent commands, flags, endpoints, tools or output:** tag commands `[doc]`/`[help]`/`[unverified]`; plans use only `[doc]`/`[help]`; unread values are `<not read>`.

## Access model
- **Reads:** `fmt -check`, `validate`, `plan`, `show`, `state list/show`, `output`, `providers`. A plan refreshes against real infrastructure, so run it with a read-only cloud/provider identity where the provider allows.
- **The plan is the change plan's core:** `terraform plan -out=<file>`, show the summary (add/change/**destroy**), and apply **that saved file** only.
- **Writes** (`apply`, `destroy`, `import`, `state mv/rm`, `force-unlock`) only as approved steps, normally from CI with a write identity enabled for the run.
- State contains secrets: never print it, never commit it.

## Risk tiers
| Tier | Examples | Gate |
|---|---|---|
| T0 read | fmt, validate, plan, show, state list/show, output, providers, `plan -refresh-only` | none |
| T1 additive | apply of a plan that only **adds** resources | plan + "approve" |
| T2 modify | apply with in-place updates, `import`, `state mv`, provider or module upgrades, `-replace` of a stateless resource | plan + "approve" per item |
| T3 destructive/irreversible | any plan with **destroy** or replace of a stateful resource, `terraform destroy`, `state rm`, `force-unlock`, backend migration, removing `prevent_destroy` | plan + typed resource address; backup first |

## Narrowest option first
- Drift: `plan -refresh-only` to see it, then decide; don't let a normal apply silently revert an incident fix.
- Rename or refactor: `moved` blocks or `state mv`, never destroy and recreate.
- Bad change: revert the commit and plan again.

## Key facts
- Removing a resource from the configuration **destroys it**, even with `prevent_destroy`.
- `state rm` forgets the object, it keeps running unmanaged.
- `force-unlock` while someone holds the lock allows two writers.
- `-auto-approve` skips the confirmation: never with a fresh, unreviewed plan.

## Rationalizations
| Thought | Reality |
|---|---|
| "I'm sure this flag exists" | Prove it: `[doc]` catalog line or `-help` this session. |
| "The plan looked fine yesterday" | Apply the saved, reviewed plan file, or plan again. |
| "Only 1 to destroy, it's minor" | Name it. A destroy of storage or a database is T3. |
| "The lock is stale, force-unlock it" | Prove nobody holds it (CI runs, colleagues). |
| "User said go" | Approval before the plan approves nothing. |

## References
- change-gate.md: plan template, **required for any change**
- command-verification.md: source tags, **required**
- terraform-command-catalog.md: [doc] forms
- terraform.md: workflow, state, locking, lifecycle, storage providers, tiers
- best-practices.md: configuration audit
- health-and-triage.md / incident-comms.md: health, playbooks, updates
- upgrade-checklist.md / upgrades-and-migration.md: Terraform and provider upgrades
