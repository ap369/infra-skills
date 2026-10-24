# Unisphere for PowerMax REST API reference (for Python development)

The **Unisphere for PowerMax 10.3** REST API reference, generated from Dell's OpenAPI spec as published in Dell's Apache-2.0 PyU4V repository. Use it to write Python code against Unisphere with plain HTTP (`requests` / `httpx`). **No Dell SDK (PyU4V) is used.**

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** Base URL, auth, versions, iterators (pagination), async jobs, destructive edits, a reusable `requests` client, safety rules. |
| [endpoints.md](endpoints.md) | Every operation (691), grouped by area, with method, path, summary and this skill's risk tier |
| [areas/](areas/) | One file per API area (25 areas): all parameters, request-body fields and responses |
| [models.md](models.md) | All 1200 request/response models with their fields |
| [spec/openapi.json](spec/openapi.json) | The spec, unmodified (Apache-2.0, see NOTICE.md) |

## How to use it (for the agent)
1. Find the operation in **endpoints.md**, then the exact parameters and body in **areas/<area>.md** and **models.md**. Those names are `[doc]` **for API version 103 (PowerMax 10.3)**. Anything not in these files is `[unverified]` (command-verification.md).
2. Check the target first: `GET /univmax/restapi/version` gives the Unisphere version and supported API versions. If the server doesn't support `103`, regenerate from the spec served by that Unisphere (`https://<unisphere>:8443/univmax/restapi/docs`). Never guess a path for another version: paths differ between `/100/`, `/101/`, `/103/`…
3. Many PUTs carry a choice of actions in the body. Tier the **action** you send, not the method (python-dev-guide.md §2).
4. Code that reads (GET) is T0. Code that writes (POST, PUT, DELETE) is a change: change-gate.md, and the safety rules in python-dev-guide.md.

## Regenerating
```
curl -sSL -o openapi.json https://raw.githubusercontent.com/dell/PyU4V/HEAD/PyU4V/tools/openapi.json
pip install pyyaml
python3 scripts/gen_api_docs.py powermax openapi.json
```
`endpoints.md`, `areas/`, `models.md` and `spec/` are regenerated. This README, `python-dev-guide.md` and `NOTICE.md` are hand-written.
