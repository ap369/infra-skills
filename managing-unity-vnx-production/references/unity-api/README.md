# Unity Unisphere Management REST API reference (for Python development)

Use this to write Python code against Dell Unity / UnityVSA with plain HTTP (`requests` / `httpx`). **No Dell SDK (storops, Ansible modules) is used.** This API is for Unity only: it does not cover VNX.

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** URL patterns, auth headers and CSRF token, queries, paging, actions, async jobs, destructive actions, a reusable `requests` client, safety rules. Committed. |
| `../unity-api-local/` | **Full** reference (every resource type, action, attribute) generated **on your machine**. Git-ignored: never commit or share it (Dell copyright). |

## How to use it (for the agent)
1. If `../unity-api-local/` exists: find the resource type or action in its `endpoints.md`, then attributes in `areas/<type>.md` and `models.md`.
2. **Provenance of the generated files.** The only public machine-readable spec we found is a **community conversion** of Dell's *Unisphere Management REST API Reference Guide* 5.4 (github.com/sachdev27/dell-unity-mcp-server, `openapi.json`). It isn't published by Dell, and its query-parameter names are missing. So: names found there are `[doc]` **only after you confirm them** in the system's own reference at `https://<unity-mgmt>/apidocs/` (or Dell's Reference Guide for your OE version). Until confirmed, mark them `[unverified]` in a change plan.
3. If `../unity-api-local/` doesn't exist: every resource, action and attribute is `[unverified]`. Point the user to `https://<unity-mgmt>/apidocs/` and the generation steps below.
4. Check the target first: `GET /api/types/basicSystemInfo/instances` (no authentication; model, name, software and API version).
5. Code that reads (GET) is T0. Code that writes (POST create/modify/actions, DELETE) is a change: change-gate.md, and the safety rules in python-dev-guide.md.

## Generate the full reference locally (never commit)
```
curl -sSL -o unity_openapi.json https://raw.githubusercontent.com/sachdev27/dell-unity-mcp-server/main/openapi.json
pip install pyyaml
python3 scripts/gen_api_docs.py unity unity_openapi.json    # writes references/unity-api-local/
```
If you have an official Dell spec for your OE version, use that file instead. `git status` must not show `unity-api-local/` (it matches `*-api-local/` in .gitignore).
