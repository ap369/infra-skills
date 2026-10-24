# Unity Unisphere Management REST API reference (for Python development)

A **Unity REST API 5.4.0** reference, generated from a community OpenAPI conversion of Dell's *Unisphere Management REST API Reference Guide*. Use it to write Python code against Dell Unity / UnityVSA with plain HTTP (`requests` / `httpx`). **No Dell SDK (storops, Ansible modules) is used.** This API is for Unity only: it does not cover VNX.

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** URL patterns, auth headers and CSRF token, queries, paging, actions, async jobs, destructive actions, a reusable `requests` client, safety rules. |
| [endpoints.md](endpoints.md) | Every operation (777), grouped by resource type, with method, path and this skill's risk tier |
| [areas/](areas/) | One file per resource type (147): actions, request-body attributes, responses |
| [models.md](models.md) | All 506 resource models with their attributes |
| [spec/unity_openapi.json](spec/unity_openapi.json) | The source file, unmodified (MIT, see NOTICE.md) |

## How to use it (for the agent)
1. Find the resource type or action in **endpoints.md**, then attributes in **areas/<type>.md** and **models.md**.
2. **Provenance:** the source is an **unofficial community conversion**, not a Dell publication, and its query-parameter names are missing. Names found here are `[doc]` **only after you confirm them** in the system's own reference at `https://<unity-mgmt>/apidocs/` (or Dell's Reference Guide for that OE version). Until then, mark them `[unverified]` in a change plan.
3. Check the target first: `GET /api/types/basicSystemInfo/instances` (no authentication; model, name, software and API version). If the OE version differs from 5.4, confirm even more carefully.
4. Code that reads (GET) is T0. Code that writes (POST create/modify/actions, DELETE) is a change: change-gate.md, and the safety rules in python-dev-guide.md.

## Regenerating
```
curl -sSL -o unity_openapi.json https://raw.githubusercontent.com/sachdev27/dell-unity-mcp-server/main/openapi.json
pip install pyyaml
python3 scripts/gen_api_docs.py unity unity_openapi.json
```
If you have an official Dell spec for your OE version, use that file instead, but check its licence before committing the output. This README, `python-dev-guide.md` and `NOTICE.md` are hand-written.
