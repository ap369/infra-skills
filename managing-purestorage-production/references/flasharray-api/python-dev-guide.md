# Python development against the FlashArray REST API (plain HTTP, no SDK)

Facts below are from the official **FlashArray REST API 2.58** OpenAPI spec (`spec/FA2.58.spec.yaml`). Look up exact paths, parameters and fields in [endpoints.md](endpoints.md), [areas/](areas/) and [models.md](models.md). **Never invent a path, parameter or field.** If it isn't in these files, it's `[unverified]` (command-verification.md).

## 1. Basics from the spec
| Topic | Spec fact |
|---|---|
| Base URL | `https://<flasharray-mgmt>`. Resources live under `/api/<version>/...` (e.g. `/api/2.58/volumes`). |
| Supported versions | `GET /api/api_version` (no authentication needed). Pick the highest 2.x version both the array and your code support. |
| Session login | `POST /api/2.58/login` with header **`api-token: <API token>`** and an empty body. The response header **`x-auth-token`** is the session token: send it as header `x-auth-token` on later calls. (Username/password in the body is allowed, but the spec says to use it only to retrieve an API token.) |
| Logout | `POST /api/2.58/logout` with header `x-auth-token` |
| OAuth 2.0 alternative | `POST /oauth2/1.0/token` (token exchange: `grant_type`, `subject_token` = a JWT ID token, `subject_token_type`). Send the access token as header `Authorization` (security scheme `OAuth2-Bearer-Token`). See *Authorization* in [areas/authorization.md](areas/authorization.md). |
| Request tracing | Optional header `X-Request-ID`. Set one per call and log it. |
| Pagination | `limit` (`limit=0` returns only `total_item_count`) and `continuation_token`, taken from the response (`continuation_token` field / `x-next-token` header). The last page has no token. **If `sort` is provided, the response doesn't include a `continuation_token`**: page with `offset` instead. If `limit` is above the system maximum, the array returns its maximum. |
| Selection | `names` / `ids` (comma-separated, can't be used together; **error if any element doesn't match**), `filter`, `sort` (`-field` for descending) |
| Partial success | Responses can be **`207`** with an `errors` list. `allow_errors=true` lets an operation continue past errors. **Always check `errors` even on 2xx.** |
| Response envelope | e.g. `VolumeGetResponse` = `continuation_token`, `more_items_remaining`, `total_item_count`, `items`, `errors` |
| Fleets | `context_names` (array of size 1) targets another array in the same fleet, or the fleet. Omit it to act on the array that received the request. |

## 2. Destructive semantics to respect (from the spec)
- **`DELETE /api/2.58/volumes` eradicates** a volume that is already destroyed: "Eradicated volumes cannot be recovered." Destroy first with `PATCH /api/2.58/volumes` body `{"destroyed": true}`; until `time_remaining` (ms) runs out, `{"destroyed": false}` recovers it. Skill tiering: destroy = T3 (recoverable), DELETE = T3, irreversible, its own approval.
- **Shrinking:** a resize to a smaller `provisioned` needs `truncate=true`. The spec says Purity takes an undo snapshot with a 24-hour window. Still T3: hosts see data loss at the end of the volume.
- `DELETE /api/2.58/connections` disconnects a volume from a host or host group: hosts lose the LUN at once (T3).
- `DELETE /api/2.58/pods` with `eradicate_contents=true` eradicates the pod's volumes, protection groups and snapshots too. Never use it without an explicit, separate approval.
- Protection group `retention_lock: ratcheted` enables SafeMode restrictions. Treat any change to it as T3 (it may not be reversible without Pure support).
- PATCH on `requested_promotion_state` (`demoted`) stops a volume accepting writes (T3 on production).
- `names` / `ids` that don't all match return an error, so lists stay exact. Never build a destroy list from a `filter` result without showing it to a human first.

## 3. Reference client (requests only)
```python
"""Minimal FlashArray REST 2.x client. Read-only by default; writes need allow_writes=True."""
import os
import uuid
import requests

class FlashArray:
    def __init__(self, host, api_token, version="2.58", ca_bundle=True, allow_writes=False, timeout=30):
        self.base = f"https://{host}"
        self.version = version
        self.allow_writes = allow_writes          # keep False for audits/monitoring
        self.timeout = timeout
        self.s = requests.Session()
        self.s.verify = ca_bundle                 # path to CA bundle; never False in production
        supported = self.s.get(f"{self.base}/api/api_version", timeout=timeout).json()["version"]
        if version not in supported:
            raise RuntimeError(f"array does not support API {version}; supports {supported[-5:]}")
        r = self.s.post(f"{self.base}/api/{version}/login", headers={"api-token": api_token}, timeout=timeout)
        r.raise_for_status()
        self.s.headers["x-auth-token"] = r.headers["x-auth-token"]   # never log this value

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
        """Iterate every item, following continuation_token (don't pass sort, or no token is returned)."""
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
        self.s.post(f"{self.base}/api/{self.version}/logout", timeout=self.timeout)

# --- read-only example (T0) ---
if __name__ == "__main__":
    fa = FlashArray(os.environ["FA_HOST"], os.environ["FA_API_TOKEN"], ca_bundle=os.environ.get("FA_CA", True))
    try:
        for v in fa.get_all("volumes", destroyed=False):
            print(v["name"], v.get("provisioned"), v.get("connection_count"))
    finally:
        fa.logout()
```
Field names in the example (`name`, `provisioned`, `connection_count`, `destroyed`) are from the `Volume` model. The `api_version` response field is `version` (model `Api_versionResponse`; FlashBlade uses `versions`). Check models.md before using any other field.

## 4. Safety rules for code that touches arrays
1. **Read-only identity and client by default.** Use an API token from a **read-only** user for monitoring and reporting code (`allow_writes=False`). Write-capable tokens live in a vault and are used only by approved change automation.
2. **Secrets:** read tokens from environment variables or a vault. Never hard-code, print or log them (`x-auth-token`, `api-token`, JWTs). Never commit them.
3. **TLS:** verify certificates (`verify=<CA bundle>`). `verify=False` is never acceptable against production.
4. **Writes go through the change gate.** The code produces a plan (exact `names`/`ids` and the exact body) for human approval, or runs only steps that are already approved. One object per call when risk is T2/T3, a read-back after each, and stop at the first error.
5. **Dry-run first:** for any write function, implement `--dry-run` that prints the method, path, params and body without sending. Use it in the change plan.
6. **Idempotence and exactness:** pass `names`/`ids`, never "everything matching a filter", for PATCH/DELETE. Re-read before acting (state may have changed). Check `connection_count` and host I/O before destroying anything.
7. **Test against a non-production array first.** Pin the API version in code and check `api_version` at start-up.
8. **Respect 207 / `errors`:** treat any `errors` entry as a failure unless the code explicitly handles partial success.
9. **Rate and load:** page with `limit` (hundreds), back off on HTTP 429/5xx, and don't poll metrics endpoints faster than needed.
