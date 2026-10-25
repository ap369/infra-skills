# ServiceNow change records and CyberArk credentials

> **Sources:** ServiceNow product documentation, *Table API* and *Change Management API* (API reference), and CyberArk *Privileged Access Manager – Self-Hosted 15.2* REST API pages (*Logon*, *Logoff*, *Get accounts*, *Get password value*, *Connect using PSM*, *Check in an exclusive account*), retrieved 2026-10-26. Endpoints and body fields named here are `[doc]`. Table **field names** beyond those listed, state values, role names and CMDB classes vary per instance: they're `[unverified]` until read from the instance (REST API Explorer, or a `GET` with `sysparm_fields`). Use whatever your organization mandates; this file describes how the change gate uses both systems.

## ServiceNow: the change record

### Rules
- **Every T1–T3 change plan cites a ServiceNow change request** (CHG number) and its **state read live**. Never invent a number, and never assume it's approved: read it. No CHG → the plan's ticket field says "none, user to supply" and the change waits (except a declared emergency, which still gets an emergency change record afterwards, as your process requires).
- The CHG's **planned start/end** is the plan's window. Outside it, stop.
- Change types in the Change Management API: **standard** (from a published template), **normal** and **emergency**. Don't hard-code state numbers: read the allowed next states for that change.
- The agent **reads** ServiceNow. Writes to ServiceNow (create a CR, add work notes, move the state, close it) change a system of record: draft them, and let the human (or an approved integration user) submit them. **Never DELETE** change requests, tasks or conflicts.

### Reads (T0)
| Purpose | Request |
|---|---|
| Find the change by number | `GET /api/now/table/change_request?sysparm_query=number=<CHG>&sysparm_fields=<fields>&sysparm_limit=1` |
| Change details (Change Management API) | `GET /api/sn_chg_rest/change/{sys_id}` |
| Allowed next states / transition conditions | `GET /api/sn_chg_rest/change/{change_sys_id}/nextstates` |
| Configuration items on the change | `GET /api/sn_chg_rest/change/{sys_id}/ci` |
| Last scheduling-conflict check result | `GET /api/sn_chg_rest/change/{sys_id}/conflict` |
| Change tasks | `GET /api/sn_chg_rest/change/{change_sys_id}/task` |
| Incident by number | `GET /api/now/table/incident?sysparm_query=number=<INC>&sysparm_fields=<fields>&sysparm_limit=1` |

- Table API parameters: `sysparm_query` (encoded query), `sysparm_fields` (comma-separated; "Invalid fields are ignored"), `sysparm_limit` with `sysparm_offset` to page, `sysparm_display_value` (display vs. actual values). Always set `sysparm_fields` and a limit: never pull whole tables ("Unusually large sysparm_limit values can impact system performance").
- **Target identity cross-check:** the CIs attached to the CHG must match the system you re-read live (array name/serial, cluster, host). A mismatch is a stop.

### Writes (drafted for the human; each its own approval)
| Action | Request | Note |
|---|---|---|
| Create a normal / emergency change | `POST /api/sn_chg_rest/change/normal`, `POST /api/sn_chg_rest/change/emergency` | standard: `POST /api/sn_chg_rest/change/standard/{standard_change_template_id}` |
| Start a scheduling-conflict check | `POST /api/sn_chg_rest/change/{sys_id}/conflict` | then read the result with `GET .../conflict` |
| Update fields / work notes | `PATCH /api/sn_chg_rest/change/{sys_id}` or `PATCH /api/now/table/change_request/{sys_id}` | field names: read them from the instance first |

**Map the change plan into the CR:** justification and impact (plan sections 1–3), implementation plan (section 4 steps), **backout plan** (the rollback column), test plan (section 6 post-checks), risk, affected CIs, planned start/end. Paste the plan's safety notice into the CR as well.

## CyberArk: the write credentials

### Rules
- **The agent never retrieves, sees, stores or prints a CyberArk password.** CyberArk's own documentation says retrieving credentials with the REST API "is intended for human use only and is not recommended for applications or automated processes"; automation uses the **Credential Providers** set up by your PAM team.
- **Interactive admin work goes through PSM** where possible (the password stays hidden and the session is recorded), or the **human** checks out the account in PVWA for the window.
- Every checkout or PSM connection carries the **reason** and the **ServiceNow CHG** as the ticket: the REST body fields are `reason`, `TicketingSystemName` and `TicketId`.
- **Exclusive accounts are checked in at the end of the window.** For accounts managed by the CPM, "after it is checked in, the password is changed immediately". Check-in is the plan's last step.
- If the policy needs approval (dual control) or a reason, wait for it. Never ask anyone to paste a password, and never put one on a command line (shell history), in a file or in chat. If a credential is exposed, treat it as compromised: check it in (CPM rotation) and say so.

### Requests (PVWA REST API, "2nd gen")
| Purpose | Request | Who |
|---|---|---|
| Log on (token; default session length 20 minutes) | `POST https://<PVWA>/PasswordVault/API/auth/{Cyberark\|LDAP\|RADIUS\|Windows}/Logon/` | the identity's owner |
| Find which account to use (needs *List Accounts* on the Safe) | `GET https://<PVWA>/PasswordVault/API/Accounts?search=<keywords>&searchType=contains` | agent may read names/metadata only |
| Connect through PSM (password not revealed) | `POST https://<PVWA>/PasswordVault/API/Accounts/{accountId}/PSMConnect/` with `reason`, `TicketingSystemName`, `TicketId`, `ConnectionComponent` | human |
| Retrieve a password (human use only) | `POST https://<PVWA>/PasswordVault/API/Accounts/{accountId}/Password/Retrieve/` with `reason`, `TicketingSystemName`, `TicketId` | **human only, never the agent** |
| Check in an exclusive account | `POST https://<PVWA>/PasswordVault/API/Accounts/{AccountID}/CheckIn/` | human (needs *Initiate CPM password management operations*) |
| Log off | `POST https://<PVWA>/PasswordVault/API/Auth/Logoff/` | the session owner |
Every call after Logon sends the session token in the `Authorization` header. Treat the token as a secret too.

## In the change plan
- **Header:** `Ticket:` = ServiceNow CHG number **and its state, read live** (e.g. `CHG0012345, state <read>`); the window from the CHG.
- **Executor:** the CyberArk account to use (Safe and account name, never the password) and how it's used (PSM session or human checkout for the window).
- **Step 0:** read the CHG (state, window, CIs) and confirm the CIs match the live target identity.
- **Last steps:** end the PSM session or check the account in; draft the CHG work notes / closure (results, deviations, post-check evidence) for the human to submit.
