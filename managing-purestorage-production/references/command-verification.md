# Command verification: no invented commands, flags, endpoints or output

Language models produce commands that look plausible but don't exist, and real commands with invented or wrong-version flags. On a production array, that is as dangerous as running the wrong command. These rules apply to **every** command, API call or MCP call shown to the user: reads, change plans, examples and "for the user to run" blocks.

## 1. Tag every command with its source (required)
Write the tag directly after the command:

| Tag | Meaning | Allowed use |
|---|---|---|
| `[doc]` | The exact form is listed in this skill's **command catalog**, or in a reference file whose verification banner says its commands were checked against vendor documentation. **You must be able to point to that line.** A file whose banner says `[unverified]` never gives `[doc]`. | Reads. Plan steps, after `[help]` confirmation on the target if the version may differ. |
| `[help]` | Confirmed **in this session** from the target system's own help or API description. Quote the matching usage line or schema. | Reads and plan steps |
| `[unverified]` | From general knowledge, or a variation of a documented command (new flag, new subcommand, different object type) | **Never executed. Never a plan step.** Only shown together with the help command that verifies it. |

If you're unsure whether something is `[doc]`, it's `[unverified]`. A similar documented command (same verb, different object or flag) doesn't make yours `[doc]`. Changing a flag, an argument order the docs don't show, or an object type (for example volume → host group) makes a `[doc]` command `[unverified]`.

## 2. Verify before you propose a change
- A change plan step may only contain `[doc]` or `[help]` commands.
- If a needed command is `[unverified]`, the plan gets a **T0 step "verify syntax"** that runs the help command. The real command is filled in, and the plan re-issued, only after the help output confirms it.
- In a draft plan, a step still waiting for verification shows a placeholder, for example `<command from "purehgroup setattr --help" output>`. **Never write the guessed command in the step, even if it's labelled.** A guessed command in a plan gets copied and run.
- If the help output doesn't show the option, **the option doesn't exist on this system**. Say so and offer the documented alternative. Never "try it and see" on production.

## 3. How to verify (read-only)
| Platform | Help / description |
|---|---|
| NetApp ONTAP CLI | `<command> ?` (parameters), `man <command>` |
| NetApp ONTAP MCP / REST | `search_ontap_endpoints`, `describe_ontap_endpoint` (MCP), or `https://<cluster>/docs/api` |
| Pure Purity CLI | `<command> --help`, `<command> <subcommand> --help` (e.g. `purevol setattr --help`) |
| Pure REST | `GET /api/api_version`, then the REST reference for that version |
| Dell symcli | `<command> -h` (e.g. `symsg -h`). The SRDF State Tables Guide covers which actions are allowed per state. |
| Dell Unisphere REST | the REST API documentation for the installed Unisphere version |
| Unity uemcli | `uemcli -d <mgmt> <object path> -help` (e.g. `/stor/prov/luns/lun -help`) |
| Unity MCP | only tools present in the tool list, with their declared schema |
| VNX | `naviseccli -help <command>`, `<nas_cmd> -help` |
| ECS / ObjectScale API | the Management REST API reference for the exact release. Use only paths in this skill's references, or ones the user confirms from that reference. |
| IBM COS Manager API | the Manager REST API / Developer Guide for the installed ClevOS release |
| Any MCP server | **only tool names present in the session's tool list**, called with their declared input schema. Never guess a tool name. |

## 4. Never invent output or state
- Every value you report (sizes, states, IDs, versions, counts, latency) must come from a tool or command output **in this session**. Cite where it came from.
- If you haven't read it, write `<not read: run X>`. Never "the output will look like…" for the user's system.
- Documentation examples may be shown only when labelled **"documentation example, not your system"**.
- In tabletop or planning mode without live access, say at the top: "No live access: values are placeholders and commands are tagged by source."

## 5. When there's no verified way
Say plainly: "I don't have a verified command for this on <platform/version>." Then give:
1. the help command to find it
2. the vendor document to check (from this skill's references)
3. the GUI path, if known from references

That's a correct answer. An invented command is not.
