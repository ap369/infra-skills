# Python development against the FlashBlade REST API (plain HTTP, no SDK)

Facts below are from the official **FlashBlade REST API 2.29** OpenAPI spec (`spec/FB2.29.spec.yaml`). Look up exact paths, parameters and fields in [endpoints.md](endpoints.md), [areas/](areas/) and [models.md](models.md). **Never invent a path, parameter or field.** If it isn't in these files, it's `[unverified]` (command-verification.md).

## 1. Basics from the spec
| Topic | Spec fact |
|---|---|
| Base URL | `https://<flashblade-mgmt-vip>`. Versioned resources live under `/api/<version>/...` (e.g. `/api/2.29/file-systems`). |
| Supported versions | `GET /api/api_version` → `{"versions": ["1.0", …, "2.29"]}`. Pick the highest 2.x version both the array and your code support. |
| Session login | `POST /api/login` with header **`api-token: <API token>`**. The response header **`x-auth-token`** is the session token. Send it as header `x-auth-token` on every later call. Body: `{"username": "..."}`. |
| Logout | `POST /api/logout` (with `x-auth-token`) |
| OAuth 2.0 alternative | `POST /oauth2/1.0/token`, form-encoded: `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, `subject_token=<JWT>`, `subject_token_type=urn:ietf:params:oauth:token-type:jwt`. The JWT comes from an API client registered on the array (see the *API Clients* area). The response's `access_token` goes in the **`Authorization: Bearer <token>`** header. |
| Request tracing | Optional header `X-Request-ID` (echoed back). Set one per call and log it. |
| Pagination | Query `limit` (`limit=0` returns only `total_item_count`) and `continuation_token`. The token for the next page comes from the response (`continuation_token` field / `x-next-token` header). **A `continuation_token` is only produced with the default sort:** if you pass `sort`, page with `offset`. |
| Selection | `names` / `ids` (comma-separated, mutually exclusive; **error if any name doesn't match**), `filter` (server-side expression), `sort` (`-field` for descending) |
| Totals | `total_item_count=true` returns the count. `total_only=true` (where supported) returns only aggregates. |
| Partial success | Some operations return **`207`** with an `errors` list (`_errorContextResponse`: `context`, `location_context`, `message`…). `allow_errors=true` lets multi-object operations continue past errors. **Always check `errors` even on 2xx.** |
| Response envelope | List responses (e.g. `FileSystemGetResponse`) = `PageInfo` (`continuation_token`, `total_item_count`) + `items` + `errors` (+ `total`) |
| Fleets | `context_names` targets another array in the same fleet. Omit it to act on the array you're connected to. |

## 2. Destructive semantics to respect (from the spec)
- **`DELETE /api/2.29/file-systems` is eradication** ("Deleting a file system is equivalent to eradication"). The file system must first be `destroyed=true` (PATCH). The skill's tiering: PATCH `destroyed=true` = T3 (recoverable during the eradication period). DELETE = T3, irreversible, its own approval.
- Many PATCH operations accept options that discard data (`discard_non_snapshotted_data`, `discard_detailed_permissions`, `delete_link_on_eradication`, `overwrite`…). Read the parameter description in the area file before using any of them.
- `names` / `ids` that don't all match return an error, so lists stay exact. Never build a delete list from a `filter` result without showing it to a human first.

## 3. Reference client (requests only)
```python
"""Minimal FlashBlade REST 2.x client. Read-only by default; writes need allow_writes=True."""
import os
import uuid
import requests

class FlashBlade:
    def __init__(self, host, api_token, version="2.29", ca_bundle=True, allow_writes=False, timeout=30):
        self.base = f"https://{host}"
        self.version = version
        self.allow_writes = allow_writes          # keep False for audits/monitoring
        self.timeout = timeout
        self.s = requests.Session()
        self.s.verify = ca_bundle                 # path to CA bundle; never False in production
        r = self.s.post(f"{self.base}/api/login", headers={"api-token": api_token}, timeout=timeout)
        r.raise_for_status()
        self.s.headers["x-auth-token"] = r.headers["x-auth-token"]   # never log this value
        supported = self.s.get(f"{self.base}/api/api_version", timeout=timeout).json()["versions"]
        if version not in supported:
            raise RuntimeError(f"array does not support API {version}; supports {supported[-5:]}")

    def _req(self, method, path, params=None, json=None):
        if method != "GET" and not self.allow_writes:
            raise PermissionError(f"write blocked ({method} {path}): client is read-only")
        rid = str(uuid.uuid4())
        r = self.s.request(method, f"{self.base}/api/{self.version}/{path.lstrip('/')}",
                           params=params, json=json, headers={"X-Request-ID": rid}, timeout=self.timeout)
        body = r.json() if r.content else {}
        if r.status_code >= 400 or body.get("errors"):
            raise RuntimeError(f"{method} {path} -> {r.status_code} (X-Request-ID {rid}): {body.get('errors')}")
        return body

    def get_all(self, path, **params):
        """Iterate every item, following continuation_token (don't pass sort, or the token isn't returned)."""
        params = {k: (",".join(v) if isinstance(v, (list, tuple)) else v) for k, v in params.items()}
        params.setdefault("limit", 500)
        while True:
            body = self._req("GET", path, params=params)
            yield from body.get("items", [])
            token = body.get("continuation_token")
            if not token:
                return
            params["continuation_token"] = token

    def logout(self):
        self.s.post(f"{self.base}/api/logout", timeout=self.timeout)

# --- read-only example (T0) ---
if __name__ == "__main__":
    fb = FlashBlade(os.environ["FB_HOST"], os.environ["FB_API_TOKEN"], ca_bundle=os.environ.get("FB_CA", True))
    try:
        for fs in fb.get_all("file-systems", destroyed=False):
            print(fs["name"], fs.get("provisioned"), fs.get("space", {}).get("virtual"))
    finally:
        fb.logout()
```
Field names in the example (`name`, `provisioned`, `space.virtual`) are from the `FileSystem` model. Check models.md before using any other field.

## 4. Safety rules for code that touches arrays
1. **Read-only identity and client by default.** Use an API token from a **read-only** account for monitoring and reporting code (`allow_writes=False`). Write-capable tokens live in a vault and are used only by approved change automation.
2. **Secrets:** read tokens from environment variables or a vault. Never hard-code, print or log them (`x-auth-token`, `api-token`, JWTs). Never commit them.
3. **TLS:** verify certificates (`verify=<CA bundle>`). `verify=False` is never acceptable against production.
4. **Writes go through the change gate.** The code produces a plan (exact `names`/`ids` and the exact body) for human approval, or runs only steps that are already approved. One object per call when risk is T2/T3, a read-back after each, and stop at the first error.
5. **Dry-run first:** for any write function, implement `--dry-run` that prints the method, path, params and body without sending. Use it in the change plan.
6. **Idempotence and exactness:** pass `names`/`ids`, never "everything matching a filter", for PATCH/DELETE. Re-read before acting (state may have changed).
7. **Test against a non-production array first**, or a FlashBlade simulator if your site has one. Pin the API version in code and check `api_version` at start-up.
8. **Respect 207 / `errors`:** treat any `errors` entry as a failure unless the code explicitly handles partial success.
9. **Rate and load:** page with `limit` (hundreds, not 0 or unlimited), back off on HTTP 429/5xx, and don't poll metrics endpoints faster than needed.
