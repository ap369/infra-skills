# Unisphere for PowerMax REST API reference (for Python development)

Use this to write Python code against Unisphere for PowerMax with plain HTTP (`requests` / `httpx`). **No Dell SDK (PyU4V) is used.**

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** Base URL, auth, versions, iterators (pagination), async jobs, destructive edits, a reusable `requests` client, safety rules. Committed. |
| `../powermax-api-local/` | **Full** reference (every endpoint, parameter, body and model) generated **on your machine** from Dell's OpenAPI spec. Git-ignored: never commit or share it (Dell copyright). |

## How to use it (for the agent)
1. If `../powermax-api-local/` exists: find the operation in its `endpoints.md`, then the exact parameters and body in `areas/<area>.md` and `models.md`. Those names are `[doc]` **for the spec's version** (shown in each file's header, e.g. PowerMax 10.3 = API version prefix `/103/`).
2. If it doesn't exist: every REST path, parameter and field is `[unverified]`. Say so, and offer the generation steps below. Never guess a path from memory: Unisphere paths differ between API versions (`/100/`, `/101/`, `/103/`…) and resources.
3. Check the target first: `GET /univmax/restapi/version` tells you the Unisphere version and the API versions it supports. Use a path prefix the server supports and the spec documents.
4. Code that reads (GET) is T0. Code that writes (POST, PUT, DELETE) is a change: change-gate.md, and the safety rules in python-dev-guide.md.

## Generate the full reference locally (never commit)
Use the spec that matches your Unisphere version. Two public sources:
- the server itself: the REST documentation can be downloaded from `https://<unisphere>:8443/univmax/restapi/docs`;
- Dell's PyU4V repository (github.com/dell/PyU4V, file `PyU4V/tools/openapi.json`, PowerMax 10.3 at the time of writing).
```
curl -sSL -o powermax_openapi.json https://raw.githubusercontent.com/dell/PyU4V/HEAD/PyU4V/tools/openapi.json
pip install pyyaml
python3 scripts/gen_api_docs.py powermax powermax_openapi.json    # writes references/powermax-api-local/
```
`git status` must not show `powermax-api-local/` (it matches `*-api-local/` in .gitignore).
