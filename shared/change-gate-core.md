# Change plan template

Every change above T0 is delivered as this document, filled in completely. Nothing gets executed until the user has approved this exact plan, whether Claude (CLI, API or MCP tool) or a human runs the commands. If any value changes after approval (target, size, object list, direction, window), the plan is re-issued and re-approved. Platform-specific notes are at the end of this file.

```markdown
## Change plan: <one-line summary>
**Target:** <system name>: <serial / SID / cluster UUID>, role <PROD | DR | TEST>, site <site>, <model, OS/code version>
**Tier:** T1 | T2 | T3   **Ticket:** <id or "none, user to supply">   **Requested by:** <user>
**Window:** <now | date/time, timezone>. Freeze calendar: <checked, no freeze | emergency exception: reason>
**Executor:** <Claude via CLI/API/MCP, one step at a time | human>

### 1. Current state (evidence)
| Check | Value | Source + timestamp |
|---|---|---|
| target identity re-read live (name + serial/UUID + role match the request) | ... | command + output |
| object identity (exact IDs) / size / used | ... | |
| who uses it (hosts, clients, apps, live I/O, recent access) | ... | |
| protection (snapshots, replication, retention/locks) | ... | |
| dependencies (other groups, clones, links, peers, mirrors) | ... | |
| capacity (pool, destination) | ... | |
| health (alerts, failed parts, rebuild/resync in progress) | ... | |
Settings this plan changes, recorded verbatim for rollback: <...>

### 2. Options considered
The narrowest option that meets the goal comes first (see the platform notes). Say why the chosen option was picked.

### 3. Impact
What changes, who is affected (hosts, clients, DR/RPO), worst case if a step goes wrong.

### 4. Steps (one change per step)
| # | Command / call (exact IDs, no wildcards or patterns) | Expected result | Rollback |
|---|---|---|---|
| 0 | safety copy (snapshot or saved config, see the platform notes) | listed / file written | n/a |
| 1 | ... | ... | ... |

### 5. Go / no-go and stop criteria
Go only if: section 1 is green, no rebuild/resync/upgrade is in progress, we are inside the window, and the approver is reachable.
Stop and report (don't improvise a fix) on: unexpected output, a new alert, a latency or error-rate jump, any object not matching the plan's IDs, or a step taking longer than 2× its expected time.

### 6. Post-checks
Reads that prove the change worked and nothing else changed.

### 7. Approval
T1/T2: "Reply **approve** to execute steps 0–N."
T3:    "Reply with the object name(s) exactly, `<name>`, to approve the irreversible/disruptive step(s)."
```

## Rules for filling it in
- **Approval is scoped to this plan.** "Go ahead", "do it now", "whatever it takes", "I approve", or a title ("I'm the manager") said *before* the plan existed approves nothing. It tells you the user wants speed, so make the plan short. It doesn't let you skip it.
- **Target identity:** re-read the system's name, serial/UUID and role live right before step 1, and again if the session was interrupted. If the user's wording is ambiguous ("the array", "prod", a hostname that could be prod or DR), or the live read doesn't match the plan, stop and ask. Never infer PROD vs. DR from a name alone.
- **Freeze and windows:** if no window is stated, or a change freeze or blackout applies (month-end, quarter-end, holidays, release freezes), ask. Outside a declared emergency, don't schedule changes into a freeze.
- **One request, many changes:** split by tier. T1 items can share one approval. Each T2/T3 item gets its own approval line.
- **Bulk operations:** list every object by its exact ID. The user approves the list shown, even if they asked not to see it: keep it compact, but show it. "Reply go for the safe set" is not an approval form.
- **Executing:** one command or call per step. Read the result (and re-query the object) before the next step. Never add flags that suppress confirmations. On an unexpected result, stop and report.
- **Emergency path (P1):** the same sections in terse form. Sections 1–3 can be 5 lines total. Approval still comes before execution. The plan text *is* the change record. Use references/incident-comms.md for status updates.
- **Secrets:** never put passwords, tokens or secret keys in the plan, the commands shown, or the output.
- **T3 extras:**
  - a second person or change board, if the site has one
  - a reversible stage (unmask, cool-off, deny policy, destroy) and the irreversible stage (eradicate, deallocate, delete, purge) are never in the same approval
  - for replication, state the **direction** explicitly in every step
