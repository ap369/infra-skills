# FlashArray REST API reference (for Python development)

The complete **FlashArray REST API 2.58** reference, generated from Pure Storage / Everpure's official OpenAPI spec. Use it to write Python code against FlashArray with plain HTTP (`requests` / `httpx`). **No Pure SDK is used.**

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** Auth, API versioning, pagination, errors, a reusable `requests` client, and safety rules for code that changes arrays. |
| [endpoints.md](endpoints.md) | Every operation (706), grouped by area, with method, path, summary and this skill's risk tier |
| [areas/](areas/) | One file per API area (81 areas): all parameters, request-body fields and responses for each operation |
| [models.md](models.md) | All 1061 request/response models with their fields (read-only fields marked) |
| [spec/FA2.58.spec.yaml](spec/FA2.58.spec.yaml) | The official OpenAPI 3.0.1 spec, unmodified (Apache-2.0, see NOTICE.md) |

## How to use it (for the agent)
1. Find the operation in **endpoints.md**. Then open its **areas/<area>.md** for the exact parameters and body fields. Look up body and response models in **models.md**.
2. Everything in these files is `[doc]` **for API version 2.58**. A path, parameter or field that isn't in these files is `[unverified]` and must not be used (command-verification.md).
3. Check what the target array supports with `GET /api/api_version`. If the array's highest version is below 2.58, only use paths and fields that exist at that version: regenerate from the matching spec (the swagger repo keeps older `FA2.<N>.spec.yaml` files).
4. Code that **reads** (GET) is T0. Code that **writes** (POST, PATCH, DELETE) is a change. Whoever runs it against a production array goes through change-gate.md, and the code must follow the safety rules in python-dev-guide.md.

## Regenerating for a new API version
```
curl -sSLO https://raw.githubusercontent.com/purestorage-openconnect/swagger/master/html/specs/FA2.<N>.spec.yaml
pip install pyyaml
python3 scripts/gen_api_docs.py flasharray FA2.<N>.spec.yaml
```
`endpoints.md`, `areas/`, `models.md` and `spec/` are regenerated. This README, `python-dev-guide.md` and `NOTICE.md` are hand-written and left alone. Update the version references in them by hand.
