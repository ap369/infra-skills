# Python development against the Unisphere for PowerMax REST API (plain HTTP, no SDK)

Facts below are from Dell's **Unisphere for PowerMax 10.3 OpenAPI spec** (title "PowerMax 10.3", as published in github.com/dell/PyU4V `PyU4V/tools/openapi.json`, retrieved 2026-10-25). Paths, parameters and fields: look them up in your local `../powermax-api-local/` (README.md). **Never invent a path, parameter or field.** If it isn't in the local reference, it's `[unverified]` (command-verification.md).

## 1. Basics from the spec
| Topic | Spec fact |
|---|---|
| Base URL | `https://<unisphere-host>:8443/univmax/restapi` (spec server: `https://localhost:8443/univmax/restapi`) |
| Auth | HTTP Basic (security scheme `apiSecurity`: `http`, `basic`) on every call. A Unisphere user with the right role, e.g. a Monitor role for read-only code. |
| Versions | `GET /version` → model `Version` (`version`, `api_Version`, `supported_Api_Versions` in the spec's model; PyU4V's docs show the response as `version`, `api_version`, `supported_api_versions`, so read both spellings). |
| Versioned paths | Most resources are under a version prefix: `/103/sloprovisioning/...`, `/103/replication/...`, `/103/system/...`, `/103/file/...`. Also `/v1/systems/{id}/...` (newer style), `/performance/...` and `/common/...`. |
| Arrays | `GET /103/system/symmetrix` lists array IDs; `GET /103/system/symmetrix/{symmetrixId}` shows one |
| Iterators (pagination) | Large list calls (e.g. `GET /103/sloprovisioning/symmetrix/{symmetrixId}/volume`) return an **`iterator`**: `id`, `count`, `maxPageSize`, `expirationTime`, and the first page in `resultList` (`result`, `from`, `to`). Get more with `GET /common/Iterator/{iteratorId}/page?from=<n>&to=<m>` (both required). Iterators expire: read them promptly. |
| `/v1` list calls | Query `select`, `filter`, `order`, `limit`, `limit_kb`, `resume_token`, `expiration_delay_secs` (e.g. `GET /v1/systems/{id}/directors`) |
| Async jobs | Many edit bodies take `executionOption`: `SYNCHRONOUS` or `ASYNCHRONOUS`. Async calls answer `202 Accepted`; follow the job with `GET /103/system/job/{jobId}` → model `job` (`status`: `SUCCEEDED`, `FAILED`, `RUNNING`, `SCHEDULED`… , `result`, `resourceLink`, `task`). |
| Errors | Typical codes in the spec: `400`, `401`, `403`, `404`, `409 Conflict`, `500` |

## 2. Destructive semantics to respect (from the spec)
- `PUT /103/sloprovisioning/symmetrix/{symmetrixId}/volume/{volumeId}` ("Choose one edit operation only per request") takes `editVolumeActionParam` with **`freeVolumeParam` ("Remove all allocations on the volume": data is gone)**, `reset_wwn_param` (hosts lose the device identity), `expandVolumeParam`, `modifyVolumeIdentifierParam`, `enable_mobility_id_param`. `freeVolumeParam` and `reset_wwn_param` are T3.
- `DELETE /103/sloprovisioning/symmetrix/{symmetrixId}/volume/{volumeId}` deletes a volume (T3, no undo).
- PUT on storage groups, masking views, port groups and host groups changes what hosts see. Removing a volume from a masked storage group or deleting a masking view takes LUNs away from hosts (T3).
- Replication (`/103/replication/...`): SnapVX restore, link/relink and SRDF actions can overwrite production data or reverse replication. Read the area file's description of every action before planning it; treat restores and SRDF failover/swap as T3.
- The generic tier in the generated files says PUT = T2. Many PowerMax PUTs carry a choice of actions in the body: tier the **action** you send, not the method.

## 3. Reference client (requests only)
```python
"""Minimal Unisphere for PowerMax REST client. Read-only by default; writes need allow_writes=True."""
import os
import time
import requests

class Unisphere:
    def __init__(self, host, user, password, api="103", port=8443, ca_bundle=True, allow_writes=False, timeout=60):
        self.base = f"https://{host}:{port}/univmax/restapi"
        self.api = api
        self.allow_writes = allow_writes          # keep False for audits/monitoring
        self.timeout = timeout
        self.s = requests.Session()
        self.s.auth = (user, password)            # Monitor role for reporting code
        self.s.verify = ca_bundle                 # path to CA bundle; never False in production
        self.s.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        v = self._req("GET", "/version")
        supported = v.get("supported_api_versions") or v.get("supported_Api_Versions") or []
        if api not in supported:
            raise RuntimeError(f"Unisphere {v.get('version')} does not support API {api}; supports {supported}")

    def _req(self, method, path, params=None, json=None):
        if method != "GET" and not self.allow_writes:
            raise PermissionError(f"write blocked ({method} {path}): client is read-only")
        r = self.s.request(method, f"{self.base}{path}", params=params, json=json, timeout=self.timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
        return r.json() if r.content else {}

    def iterate(self, path, **params):
        """Yield every result of a list call that returns an iterator."""
        it = self._req("GET", f"/{self.api}{path}", params=params or None)
        page = it.get("resultList", {})
        yield from page.get("result", [])
        last, count, size = page.get("to", 0), it.get("count", 0), it.get("maxPageSize", 1000)
        while it.get("id") and last < count:
            page = self._req("GET", f"/common/Iterator/{it['id']}/page",
                             params={"from": last + 1, "to": min(last + size, count)})
            yield from page.get("result", [])
            last = page.get("to", count)

    def wait_job(self, job_id, poll=5, limit=1800):
        end = time.time() + limit
        while time.time() < end:
            job = self._req("GET", f"/{self.api}/system/job/{job_id}")
            if job["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "VALIDATE_FAILED", "INVALID"):
                if job["status"] != "SUCCEEDED":
                    raise RuntimeError(f"job {job_id} {job['status']}: {job.get('result')}")
                return job
            time.sleep(poll)
        raise TimeoutError(f"job {job_id} still running after {limit}s: check it before doing anything else")

# --- read-only example (T0) ---
if __name__ == "__main__":
    u = Unisphere(os.environ["U4P_HOST"], os.environ["U4P_USER"], os.environ["U4P_PASSWORD"],
                  ca_bundle=os.environ.get("U4P_CA", True))
    for sid in u._req("GET", f"/{u.api}/system/symmetrix").get("symmetrixId", []):
        print("array", sid)
        for vol in u.iterate(f"/sloprovisioning/symmetrix/{sid}/volume", mapped="true"):
            print("  ", vol)
```
Names used: `listSymmetrixResult.symmetrixId`, the volume list's `mapped` filter, `iterator` / `resultList` fields, and the `job.status` enum are all in the spec's models. **Check the iterator page bounds** (`from` = previous `to` + 1) with one test read on a non-production Unisphere before relying on it: the spec gives the parameters but not their indexing.

## 4. Safety rules for code that touches arrays
1. **Read-only role by default** (Monitor) for reporting code (`allow_writes=False`). Write-capable credentials live in a vault and are used only by approved change automation.
2. **Secrets:** read credentials from environment variables or a vault. Never hard-code, print or log them. Never commit them.
3. **TLS:** verify certificates (`verify=<CA bundle>`). `verify=False` is never acceptable against production.
4. **Writes go through the change gate.** The code produces a plan (exact method, path, array ID, object IDs and body) for human approval, or runs only approved steps. One edit per request (the API requires it for volumes), one object per call for T2/T3, wait for the job, read back, stop at the first error.
5. **Dry-run first:** for any write function, implement `--dry-run` that prints the method, path and body without sending.
6. **Right array, every call:** put the `symmetrixId` in the plan and assert it in code. Unisphere can manage several arrays: a wrong ID hits the wrong array.
7. **Test against a non-production array / Unisphere first.** Pin the API version (`/103/`) and check `/version` at start-up.
8. **Rate and load:** don't poll performance or job endpoints faster than needed; Unisphere is shared with the GUI and other tools.
