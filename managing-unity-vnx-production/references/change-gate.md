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
| who uses it (masking/host access, logins, live I/O, NFS/SMB clients) | ... | |
| protection (snapshots, linked targets, SRDF/replication both sides) | ... | |
| dependencies (other SGs/storage groups, parent SGs, attached snapshots) | ... | |
| capacity (pool/SRP, destination) | ... | |
| array health (events, failed parts, SP/director state) | ... | |
Settings this plan changes, recorded verbatim for rollback: <...>

### 2. Options considered
The narrowest option that meets the goal comes first. Examples: unmask before deallocate, gold copy before resync, expand before deleting snapshots, linked snapshot before restore. Say why the chosen option was picked.

### 3. Impact
What changes, who is affected (clients, hosts, DR/RPO), worst case if a step goes wrong.

### 4. Steps (one change per step)
| # | Command (exact IDs, no wildcards or patterns) | Expected result | Rollback |
|---|---|---|---|
| 0 | safety snapshot: SnapVX / Unity / VNX snapshot named <ticket> | snapshot listed | n/a |
| 1 | ... | ... | ... |

### 5. Post-checks
Reads that prove the change worked and nothing else changed (masking/host access, paths, replication state, latency).

### 6. Approval
T1/T2: "Reply **approve** to execute steps 0–N."
T3:    "Reply with the object name(s) exactly — `<name>` — to approve the irreversible/disruptive step(s)."
```

## Rules for filling it in
- **Approval is scoped to this plan.** "Go ahead", "do it now", "whatever it takes", "I approve", or a title ("I'm the infra manager") said *before* the plan existed approves nothing. It tells you the user wants speed, so make the plan short. It doesn't let you skip it.
- **One request, many changes:** split by tier. T1 items can share one approval. Each T2/T3 item gets its own approval line.
- **Bulk operations:** list every object by its exact ID (device hex ID, snapshot ID, LUN ID). The user approves the list shown, even if they asked not to see it: keep it compact, but show it. Execute one object at a time, with a read after each, and stop at the first surprise.
- **Executing:** one command per step. Read the result (and re-query the object) before the next step. Never add `-noprompt`, `-force` or `-symforce` to skip confirmations. On an unexpected result, stop and report. Don't improvise a fix.
- **Emergency path (P1):** the same sections in terse form. Sections 1–3 can be 5 lines total. Approval still comes before execution. The plan text *is* the change record.
- **T3 extras:**
  - a second person or change board, if the site has one
  - unmask/remove access (reversible) and deallocate/delete (irreversible) are never in the same approval
  - "reply go for the safe set" is not an approval form: the user approves the objects listed in the plan
  - for SRDF/MirrorView/replication, state the **direction** explicitly in every step (R1 → R2)
