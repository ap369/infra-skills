# ONTAP / ASA r2 REST API reference (for Python development)

Use this to write Python code against ONTAP (FAS, AFF, ASA) and ASA r2 with plain HTTP (`requests` / `httpx`). **No NetApp SDK (`netapp_ontap`) is used.**

| File | What it holds |
|---|---|
| [python-dev-guide.md](python-dev-guide.md) | **Start here.** Auth, fields, queries, pagination, async jobs, errors, ASA r2 differences, a reusable `requests` client, safety rules. Facts are from NetApp's official REST docs. |
| [endpoints.md](endpoints.md) | **Read-only** reference (committed): 212 GET endpoints for ONTAP 9.16, with the version each appeared in |
| [areas/](areas/) | Per area: each GET endpoint's filters and fields, with *since* versions |
| [spec/](spec/) | NetApp's ontap-mcp catalog (Apache-2.0, see NOTICE.md) |
| `../ontap-api-local/`, `../asa-api-local/` | **Full** reference (every method, body and model) generated **on your machine** from your system's own swagger. Git-ignored: never commit it (NetApp copyright). |

## How to use it (for the agent)
1. **Reads:** a path, filter or field in endpoints.md / areas/ is `[doc]` for ONTAP 9.16 (watch the *since* column on older clusters). A GET endpoint not in the catalog is `[unverified]` unless it's in a local full reference.
2. **Writes (POST / PATCH / DELETE):** the committed catalog has none. Use them only if `../ontap-api-local/` (or `../asa-api-local/` for ASA r2) exists and lists the exact method, path and body field; then they are `[doc]` for that system's version. Otherwise a write call is `[unverified]`: say so, and point the user to the regeneration steps below or to `https://<cluster-mgmt>/docs/api`.
3. Check the target's version first: `GET /api/cluster/nodes?fields=version` (`version.full`, `version.generation`, `version.major`, `version.minor` are catalog filters for `/cluster/nodes`).
4. Code that reads is T0. Code that writes is a change: change-gate.md, and the safety rules in python-dev-guide.md.

## Full API locally (ONTAP or ASA r2): never commit
The cluster serves its own API reference: Swagger UI at `https://<cluster-mgmt>/docs/api` (sign in with an account allowed to use the REST API). The spec file behind it is what NetApp's ontap-mcp generator reads (`/docs/api/swagger.yaml`); if your version serves it elsewhere, download it from the Swagger UI page.
```
curl -sS --cacert <ca.pem> -u <readonly-user> -o swagger.yaml https://<cluster-mgmt>/docs/api/swagger.yaml
pip install pyyaml
python3 scripts/gen_api_docs.py ontap swagger.yaml     # writes references/ontap-api-local/
python3 scripts/gen_api_docs.py asa   swagger.yaml     # for an ASA r2 system: writes references/asa-api-local/
```
`git status` must not show these folders (they match `*-api-local/` in .gitignore). Don't share them outside your organization.

## Regenerating the committed catalog
```
curl -sSLO https://raw.githubusercontent.com/NetApp/ontap-mcp/main/conf/ontap_api_catalog.json
python3 scripts/gen_ontap_catalog_docs.py ontap_api_catalog.json
```
