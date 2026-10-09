# Change plan template

Every change above T0 is delivered as this document, filled in completely. Nothing gets executed until the user has approved this exact plan, whether Claude or a human runs the commands. If any value changes after approval (target, size, snapshot, direction), the plan is re-issued and re-approved.

```markdown
## Change plan: <one-line summary>
**Array(s):** <name/SID> (<model>, <OE/code version>)   **Tier:** T1 | T2 | T3   **Ticket:** <id or "none — user to supply">
**Requested by:** <user>   **Window:** <now | date/time, business impact>
**Executor:** Claude via CLI (one step at a time) | human

### 1. Current state (evidence)
| Check | Value | Source + timestamp |
|---|---|---|
| object identity (exact IDs) / size / used | ... | command + output |
| who uses it (object users with keys, recent access, still-writing check) | ... | |
| protection (versioning, Object Lock, retention, legal holds, geo replication) | ... | |
| dependencies (apps using the user/keys, replication or backup targets) | ... | |
| capacity (storage pool, GC backlog, quotas) | ... | |
| array health (alerts, nodes, disks, RG status) | ... | |
Settings this plan changes, recorded verbatim for rollback: <...>

### 2. Options considered
The narrowest option that meets the goal comes first. Examples: deny-all cool-off before emptying a bucket, second key before deleting a leaked one, GOVERNANCE or a test bucket before COMPLIANCE, prefix-scoped lifecycle before a bucket-wide one. Say why the chosen option was picked.

### 3. Impact
What changes, who is affected (clients, hosts, DR/RPO), worst case if a step goes wrong.

### 4. Steps (one change per step)
| # | Command (exact IDs, no wildcards or patterns) | Expected result | Rollback |
|---|---|---|---|
| 0 | save current config (policy, lifecycle, quota, retention) to a file named <ticket> | file written | n/a |
| 1 | ... | ... | ... |

### 5. Post-checks
Reads that prove the change worked and nothing else changed (config re-read, access works or is denied as intended, replication and alerts).

### 6. Approval
T1/T2: "Reply **approve** to execute steps 0–N."
T3:    "Reply with the object name(s) exactly — `<name>` — to approve the irreversible/disruptive step(s)."
```

## Rules for filling it in
- **Approval is scoped to this plan.** "Go ahead", "do it now", "whatever it takes", "I approve", or a title ("I'm the infra manager") said *before* the plan existed approves nothing. It tells you the user wants speed, so make the plan short. It doesn't let you skip it.
- **One request, many changes:** split by tier. T1 items can share one approval. Each T2/T3 item gets its own approval line.
- **Bulk operations:** list every object by its exact ID (namespace/bucket, user, key timestamp). The user approves the list shown, even if they asked not to see it: keep it compact, but show it. Execute one object at a time, with a read after each, and stop at the first surprise.
- **Executing:** one command per step. Read the result (and re-query the object) before the next step. Never print tokens or secrets in commands or output. On an unexpected result, stop and report. Don't improvise a fix.
- **Emergency path (P1):** the same sections in terse form. Sections 1–3 can be 5 lines total. Approval still comes before execution. The plan text *is* the change record.
- **T3 extras:**
  - a second person or change board, if the site has one
  - cool-off (reversible) and empty/delete (irreversible) are never in the same approval; deletions need the data owner's written sign-off
  - "reply go for the safe set" is not an approval form: the user approves the objects listed in the plan
  - for geo-replicated buckets, state the **direction** explicitly in every step (which VDCs are affected)
