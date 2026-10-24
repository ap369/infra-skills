# infra-skills

[![License: MIT](https://img.shields.io/github/license/ap369/infra-skills)](LICENSE)
[![Claude Code Skills](https://img.shields.io/badge/Claude_Code-skills-D97757)](https://docs.claude.com/en/docs/claude-code/skills)
[![OpenCode Skills](https://img.shields.io/badge/OpenCode-skills-211E1E)](https://opencode.ai/docs/skills/)
[![Skills](https://img.shields.io/badge/skills-6-blue)](#infra-skills)

Agent skills (Claude Code, OpenCode) for operating infrastructure in production.

> [!CAUTION]
> ## ⚠️ READ BEFORE USING THESE SKILLS ON ANY ARRAY ⚠️
> **Modifying a production storage array is never 100% safe, with or without these skills.** A single wrong command can cause an outage or **permanent, unrecoverable data loss** across every host, application and site that depends on the array.
>
> - **These skills reduce risk. They don't eliminate it.** Approval gates, safety snapshots, staged deletes and read-only defaults lower the chance of a mistake, but they can't guarantee a safe outcome.
> - **Commands and values are NOT validated** against your arrays, firmware or versions. They come from general vendor knowledge and can be wrong, outdated or unsupported in your environment.
> - **An AI agent can be wrong**, misread output, or pick the wrong object or the wrong array. **You** are responsible for every change you approve. Read every command before approving it.
> - **Before any change:** have verified backups, test in non-production first, follow your change management process, check the vendor's current documentation, and involve vendor support for upgrades, failovers and anything irreversible.
> - **Use read-only access by default.** Give an agent write credentials only for an approved change window, and revoke them afterwards.
> - **No warranty, no liability.** Provided "AS IS" under the MIT license. The authors and contributors accept no liability for outages, data loss or any other damage arising from the use of these skills.
>
> **If you aren't prepared to own the outcome of a change, don't approve it.**


| Skill | Scope |
|---|---|
| `managing-purestorage-production` | Pure Storage FlashArray, FlashBlade, Pure1 and Pure Fusion. Read-only by default (via the Pure Fusion MCP server); every change goes through a gated, approved change plan. ActiveCluster/ActiveDR and security content checked against the **Everpure public docs (retrieved 2026-10-13)**. |
| `managing-netapp-production` | NetApp ONTAP (AFF/FAS/ASA), StorageGRID, BlueXP. Uses NetApp's ONTAP MCP server (`--read-only` recommended); every change, including MCP write tools, goes through a gated, approved change plan. Verified against the **ONTAP 9 documentation (generated 2026-10-08, up to ONTAP 9.19.1)**: see [Sources](#sources-and-documentation-versions). |
| `managing-powermax-production` | Dell PowerMax and VMAX (VMAX3, All Flash, 10K/20K/40K). Read-only symcli as a Monitor-role identity; every change goes through a gated, approved change plan. Checked against **Dell Solutions Enabler 10.4 / PowerMaxOS 10 docs (Apr 2026)**. |
| `managing-unity-vnx-production` | Dell Unity / Unity XT and VNX (block and file). Unity via a GET-only community MCP server plus uemcli; VNX via naviseccli and Control Station; every change goes through a gated, approved change plan. |
| `managing-ecs-objectscale-production` | Dell ECS / ObjectScale object storage (S3). Read-only Management API (System Monitor) and config-only S3 reads, no secrets in transcripts; every change goes through a gated, approved change plan. |
| `managing-ibm-cos-production` | IBM Cloud Object Storage on-prem (Cleversafe dsNet). Read-only Manager API and config-only S3 reads, IDA margin math before any device work; every change goes through a gated, approved change plan. |

## How the skills work

Every skill follows the same model:

- **Reading is free, changing is gated.** The agent reads through read-only identities (MCP servers in read-only mode, Monitor / Operator / Read Only roles). Every change, whatever the executor (CLI, API, MCP write tool or human), is delivered as a **change plan** and runs only after the user approves *that* plan.
- **Risk tiers:**
  - **T0 read:** no approval
  - **T1 additive:** "approve"
  - **T2 modify:** "approve" per item
  - **T3 destructive or disruptive:** the user types the object name, a safety copy is taken first, and the reversible and irreversible stages get separate approvals
- **The change plan** (`references/change-gate.md`) contains:
  - the target identity (name, serial/UUID, PROD/DR role) re-read live
  - evidence and options considered
  - impact
  - exact steps with a rollback for each
  - go/no-go and stop criteria
  - post-checks
  - freeze-calendar awareness
- **Narrowest option first.** For example: unmask before deallocate, FlexClone before a SnapMirror break, a cool-off period before deleting a bucket, one device at a time within the erasure-coding margin.
- **Each skill includes:**
  - a best-practice configuration audit
  - health checks
  - incident playbooks and communication templates
  - an upgrade checklist, and migration / tech-refresh guidance

## Disclaimer

**No change to a storage array is 100% safe.** See the caution notice at the top of this page. In addition:

- Commands, API paths and recommended values come from general vendor knowledge. **They are not validated against your systems or versions.** The skills tell the agent to confirm syntax (`--help` / API reference) and values against current vendor documentation, and site standards override the defaults.
- Every change plan the agent produces ends with a **safety notice**. Approving a plan means you have read the commands and accept responsibility for running them.
- The skills are not a substitute for backups, change management, vendor support, or a qualified storage engineer reviewing the change.
- Provided "AS IS" under the MIT license, without warranty of any kind. The authors accept no liability for outages, data loss or other damage.

## Sources and documentation versions

| Skill | Vendor documentation used | Version / date | Notes |
|---|---|---|---|
| `managing-netapp-production` | [ONTAP 9 documentation (full-site PDF)](https://docs.netapp.com/us-en/ontap/pdfs/fullsite-sidebar/ONTAP_9_documentation.pdf) | Generated by NetApp on **2026-10-08**, latest release covered **ONTAP 9.19.1**, 3,247 pages. Retrieved 2026-10-13. | Commands, versions and defaults checked against it. References cite PDF page numbers (`pN`). The PDF doesn't include the full CLI man pages or the login-only release notes. |
| `managing-netapp-production` (MCP) | [NetApp/ontap-mcp](https://github.com/NetApp/ontap-mcp) docs (`docs/tools.md`, `docs/install.md`) | `main` branch as of 2026-10-09 | Tool names, `--read-only`, tool modes |
| `managing-purestorage-production` | Everpure (formerly Pure Storage) **public** documentation at [support.everpuredata.com](https://support.everpuredata.com): ActiveCluster, ActiveDR (incl. VMware and Oracle guides), FlashArray Security, Directory Services on FlashArray, FlashArray Block best practices, FlashArray File Services, Purity//FA REST API, and the FlashArray security bulletins (CVE-2023-28373 … CVE-2026-6445) | Retrieved **2026-10-13** (171 topics plus 7 bulletins). Content covers Purity//FA up to 6.12.x (ActiveCluster File 6.12.2+). | Summarized with source names. The **Purity//FA Admin & CLI Reference Guide is not public**, so most CLI syntax is still unverified (11 of 69 commands confirmed). Pages marked "Restricted – Do Not Distribute" (self-service upgrade procedures) and "Confidential" (technical briefs) were **not** used. |
| `managing-purestorage-production` (FlashBlade REST API) | Official **FlashBlade REST API 2.29** OpenAPI spec from [purestorage-openconnect/swagger](https://github.com/purestorage-openconnect/swagger) (Apache-2.0) | Retrieved **2026-10-25** | Full generated reference (661 operations, 100 areas, 977 models) in `references/flashblade-api/`, plus a Python guide using plain `requests` (no SDK). Regenerate with `scripts/gen_flashblade_api_docs.py`. |
| `managing-purestorage-production` (MCP) | [Pure Fusion MCP Server sneak peek](https://blog.everpuredata.com/products/a-sneak-peek-at-the-pure-fusion-mcp-server/) (Pure blog) | read 2026-10-09 | |
| `managing-unity-vnx-production` (MCP) | [sachdev27/dell-unity-mcp-server](https://github.com/sachdev27/dell-unity-mcp-server) README | as of 2026-10-09 | Community server; credentials passed per call |
| `managing-powermax-production` | Dell **public** PDFs on dl.dell.com (index: Dell KB 000189115 / 000226772): Solutions Enabler **10.4.0** SRDF Family CLI User Guide, Array Controls and Management CLI User Guide, SRDF State Tables Guide, Installation Guide, What's new 10.4.0; TimeFinder SnapVX CLI User Guide 10.0.0 (latest; no SnapVX changes in 10.4); PowerMax Family Security Configuration Guide (PowerMaxOS 10) and Product Guide; SRDF Introduction; SRDF/Metro vWitness Configuration Guide; Events and Alerts 10.3.0 | Docs dated Jul 2022 → **Apr 2026**, retrieved **2026-10-14**. Covers Solutions Enabler 10.4 / PowerMaxOS 10. | Commands checked against the guides (`-slo` → `-sl`, `symdisk list -failed` replaced, `free -all` preconditions). `symstat` and `symgate` are only in the online CLI Reference (developer.dell.com, not fetchable), so they're marked unverified. PowerMaxOS and SE **release notes need a Dell login** and weren't used. |
| `managing-ecs-objectscale-production`, `managing-ibm-cos-production` | none (general vendor knowledge) | n/a | **Not validated against a specific documentation release.** Check commands with `-h` / `--help` / the API reference for your version. |

When a newer vendor documentation release comes out, re-verify the skill against it and update this table. For NetApp, re-run the command cross-check against the new PDF and refresh `ontap-versions-and-defaults.md`.

## Install

```
git clone https://github.com/ap369/infra-skills.git ~/infra-skills
```

### Claude Code

Symlink each skill into your personal skills directory:

```
mkdir -p ~/.claude/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.claude/skills/managing-purestorage-production
ln -s ~/infra-skills/managing-netapp-production ~/.claude/skills/managing-netapp-production
ln -s ~/infra-skills/managing-powermax-production ~/.claude/skills/managing-powermax-production
ln -s ~/infra-skills/managing-unity-vnx-production ~/.claude/skills/managing-unity-vnx-production
ln -s ~/infra-skills/managing-ecs-objectscale-production ~/.claude/skills/managing-ecs-objectscale-production
ln -s ~/infra-skills/managing-ibm-cos-production ~/.claude/skills/managing-ibm-cos-production
```

### OpenCode

OpenCode reads skills from `~/.config/opencode/skills/` (global) or `.opencode/skills/` (per project). It also reads `~/.claude/skills/`, so if you already did the Claude Code install, you're done.

```
mkdir -p ~/.config/opencode/skills
ln -s ~/infra-skills/managing-purestorage-production ~/.config/opencode/skills/managing-purestorage-production
ln -s ~/infra-skills/managing-netapp-production ~/.config/opencode/skills/managing-netapp-production
ln -s ~/infra-skills/managing-powermax-production ~/.config/opencode/skills/managing-powermax-production
ln -s ~/infra-skills/managing-unity-vnx-production ~/.config/opencode/skills/managing-unity-vnx-production
ln -s ~/infra-skills/managing-ecs-objectscale-production ~/.config/opencode/skills/managing-ecs-objectscale-production
ln -s ~/infra-skills/managing-ibm-cos-production ~/.config/opencode/skills/managing-ibm-cos-production
```

Optional: control skill access in `opencode.json`:

```json
{
  "permission": {
    "skill": { "managing-*-production": "allow" }
  }
}
```

## Prerequisites: MCP servers

### Pure Fusion MCP server (Pure Storage skill)

1. Get the server binary from github.com/purestorage-openconnect. Run its config command with **read-only** API tokens from each array.
2. Register it with your agent:
   - **Claude Code:** `claude mcp add pure-fusion -- <path-to-binary> --config <config-file>`
   - **OpenCode:** add it to `opencode.json`:
     ```json
     {
       "mcp": {
         "pure-fusion": {
           "type": "local",
           "command": ["<path-to-binary>", "--config", "<config-file>"],
           "enabled": true
         }
       }
     }
     ```

See `managing-purestorage-production/references/fusion-and-pure1.md` for details.

### ONTAP MCP server (NetApp skill)

1. Write `ontap.yaml` with your clusters under `Pollers:` (see [NetApp/ontap-mcp](https://github.com/NetApp/ontap-mcp)). Use an ONTAP user with a **read-only** role.
2. Start the server in read-only mode, bound to localhost:
   ```
   docker run -d --name ontap-mcp-ro -p 127.0.0.1:8083:8083 \
     -v ~/.config/ontap-mcp/ontap.yaml:/opt/mcp/ontap.yaml:ro \
     ghcr.io/netapp/ontap-mcp:latest start --port 8083 --host 0.0.0.0 --read-only
   ```
3. Register it with your agent:
   - **Claude Code:** `claude mcp add --transport http ontap-mcp http://127.0.0.1:8083`
   - **OpenCode:** add it to `opencode.json`:
     ```json
     {
       "mcp": {
         "ontap-mcp": { "type": "remote", "url": "http://127.0.0.1:8083", "enabled": true }
       }
     }
     ```

See `managing-netapp-production/references/ontap-mcp-and-bluexp.md` for details.

### Dell PowerMax / VMAX (no MCP)

There is no production-grade MCP server for PowerMax/VMAX. The agent runs read-only `symcli` commands on a management host with Solutions Enabler installed. Map that OS user to a **Monitor** role (symauth / Unisphere user authorization) so write commands are refused by the array. See `managing-powermax-production/references/access-and-tools.md`.

### Dell Unity MCP server (community) and VNX CLI

1. Create a dedicated Unity account with the **Operator** (read-only) role. The community server ([sachdev27/dell-unity-mcp-server](https://github.com/sachdev27/dell-unity-mcp-server)) passes the password on every tool call, so it ends up in agent transcripts.
2. Install and register it, GET-only, with TLS verification on:
   - **Claude Code:**
     ```
     pip install dell-unity-mcp-server
     claude mcp add unity -e ALLOWED_HTTP_METHODS=GET -e UNITY_TLS_VERIFY=true -- python -m unity_mcp.main
     ```
   - **OpenCode:** add it to `opencode.json`:
     ```json
     {
       "mcp": {
         "unity": {
           "type": "local",
           "command": ["python", "-m", "unity_mcp.main"],
           "environment": { "ALLOWED_HTTP_METHODS": "GET", "UNITY_TLS_VERIFY": "true" },
           "enabled": true
         }
       }
     }
     ```
3. Save read-only `uemcli` credentials (`-saveUser`) for each array. For VNX, create a `naviseccli` security file for a read-only account.

See `managing-unity-vnx-production/references/access-and-tools.md`.

### Dell ECS / ObjectScale (no MCP)

There is no MCP server for ECS. The agent reads through its shell:
- **Management API** (port 4443), as a dedicated **System Monitor** user. Keep its password in a mode-600 file or a vault.
- **`aws s3api get-*`**, with an `ecs-ro` profile that can only read bucket configuration.

See `managing-ecs-objectscale-production/references/access-and-tools.md`.

### IBM Cloud Object Storage / Cleversafe (no MCP)

There is no MCP server for on-prem dsNet. The existing IBM COS MCP servers target IBM Cloud, not a dsNet Manager. The agent reads through its shell:
- **Manager REST API**, as a dedicated **Read Only** role user.
- **`aws s3api get-*`**, with a `cos-ro` profile pointing at the Accessers.

See `managing-ibm-cos-production/references/access-and-tools.md`.

## Third-party content

The repository is MIT-licensed, except `managing-purestorage-production/references/flashblade-api/spec/FB2.29.spec.yaml`, which is Pure Storage / Everpure's FlashBlade REST API spec under the **Apache License 2.0** (license and attribution in that folder's `spec/LICENSE` and `NOTICE.md`).

## Repository layout

```
managing-<platform>-production/   one skill per platform (SKILL.md + references/)
shared/                           change-gate core, incident comms, upgrade checklist
                                  (synced into every skill by scripts/sync_shared.py)
scripts/sync_shared.py            copy shared files into each skill (--check for CI)
scripts/lint_skills.py            frontmatter, references, shared copies, README, tests
scripts/gen_flashblade_api_docs.py  regenerate the FlashBlade REST API reference from a spec
tests/                            pressure scenarios and pass criteria per skill
.github/workflows/                lint + skills-count badge
```

## Contributing / adding a skill

1. **Baseline first:** write 3–4 pressure scenarios in `tests/<skill>.md` and run them on an agent **without** the skill (see `tests/README.md`). Record what it gets wrong.
2. Create `managing-<platform>-production/SKILL.md`, with the same sections as the existing skills and ≤ 500 words, plus `references/`. Put platform notes under the marker in `references/change-gate.md`.
3. Run `python3 scripts/sync_shared.py`, then `python3 scripts/lint_skills.py`.
4. Re-run the scenarios **with** the skill until every pass criterion holds.
5. Add the README table row and the symlink lines, then open a PR. CI runs the lint, and the skills badge updates itself.

Edit shared content only in `shared/`, never in a skill's copy, then re-run the sync.
