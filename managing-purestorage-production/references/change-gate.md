# Change plan template

Every change above T0 is delivered as this document, filled in completely. Nothing gets executed until the user has approved this exact plan. If any value changes after approval (target, size, retention, schedule), the plan is re-issued and re-approved.

```markdown
## Change plan: <one-line summary>
**Array(s):** <name> (<FA|FB>, Purity <version>)   **Tier:** T1 | T2 | T3   **Ticket:** <id or "none — user to supply">
**Requested by:** <user>   **Window:** <now | date/time, business-hours impact>

### 1. Current state (evidence)
| Check | Value | Source + timestamp |
|---|---|---|
| object exists / size / used | ... | MCP tool or CLI output |
| host connections / LUN ids | ... | |
| live I/O (and history if available) | ... | |
| pgroup / pod / replica membership | ... | |
| pending-eradication + SafeMode state | ... | |
| capacity headroom (local and target) | ... | |
Settings this plan changes, recorded verbatim for rollback: <...>

### 2. Impact
What changes, who is affected (hosts, apps, DR/RPO), worst-case outcome if a step goes wrong.

### 3. Steps (one change per step)
| # | Command (exact, no wildcards) | Expected result | Rollback |
|---|---|---|---|
| 0 | safety snapshot: `purevol snap --suffix <ticket>` / `purepgroup snap --suffix <ticket>` | snapshot listed | n/a |
| 1 | ... | ... | ... |

### 4. Post-checks
Commands that prove the change worked and nothing else changed (connections, I/O, pod status, replication).

### 5. Approval
T1/T2: "Reply **approve** to execute steps 0–N."
T3:    "Reply with the object name(s) exactly — `<name>` — to approve the irreversible/disruptive step(s)."
```

## Rules for filling it in
- **Approval is scoped to this plan.** "Go ahead", "I approve", "do it" or a title ("I'm the storage lead") said *before* the plan existed approves nothing. Present the plan and get approval for it.
- **One request, many changes:** split by tier. Additive parts (T1) can be approved together. Each T2 or T3 part gets its own approval line. Never let the approval for an easy part carry a risky part along with it.
- **Executor:** the Fusion MCP server is read-only, so a human runs the commands. Present them as a copy-paste block and ask for the output back, then run the post-checks through MCP. If write tools exist in the session, they still execute only after approval, one step at a time, with a read between steps.
- **Emergency path:** keep the same sections in terse form. Section 1 can be 3 lines. Approval still comes before execution. Fill the ticket in afterwards, but the plan text *is* the record, so keep it.
- **No snapshot possible** (FB bucket, config-only change): say so in step 0 and give the alternative (exported config, recorded settings).
- **T3 extras:**
  - a second person or change board is suggested if the site has one
  - a wait of at least 24h between destroy and eradicate unless the user insists *after* seeing the list
  - never eradicate as part of the same approval as destroy
