# Python development against the ONTAP / ASA r2 REST API (plain HTTP, no SDK)

Sources: NetApp's official *Getting started with the ONTAP REST API* (docs.netapp.com/us-en/ontap-restapi, page dated 2026-10-13) and *REST API support for ASA r2* (docs.netapp.com/us-en/asa-r2, 2026-08-26), retrieved 2026-10-25; endpoint, filter and field names from [endpoints.md](endpoints.md) / [areas/](areas/). **Never invent a path, filter or field.** If it isn't in these files or in your local full reference (`../ontap-api-local/`), it's `[unverified]` (command-verification.md).

## 1. Basics from NetApp's docs
| Topic | Fact |
|---|---|
| Base URL | `https://<cluster-mgmt-LIF>/api/...` (e.g. `/api/storage/volumes`) |
| Auth | HTTP Basic (`curl -u <username>:<password>` in NetApp's examples). OAuth 2.0: the ASA r2 page documents passing the access token as a bearer token in the `Authorization` header; for unified ONTAP check your version's docs before relying on it. **401** = authentication failed, **403** = RBAC refused. |
| API reference on the system | Swagger UI at `https://<cluster-mgmt>/docs/api` |
| Fields | Collection GETs return only `name` and `uuid` by default. Ask for more with `fields=a,b.c` (`fields=b.{c,d}`, `fields=b,!b.c` also work). `fields=*` leaves out *expensive* properties. `ignore_unknown_fields=true` stops an error for a field unknown on that version. |
| Queries | `<field>=<value>` filters by value. Quote values that contain query characters (`*\|,!<>..`). |
| Sorting | `order_by=<field> [asc\|desc]` (sorting can make the call slower) |
| Pagination | `max_records=<n>` limits records per response; the response then has `_links.next.href` (and a `Link: ...; rel="next"` header). Follow it until there's no `next`. `offset` skips records. `num_records` is the count in the response. |
| Timeouts | `return_timeout=<0..120>` seconds. Operations expected to take under 2 s are synchronous and ignore it. |
| Async jobs | A non-blocking operation that isn't done within `return_timeout` returns **202 Accepted** with a `job` object (`uuid`, `_links.self.href` → `/api/cluster/jobs/<uuid>`). Poll the job until its `state` is `success` or `failure` (`/api/cluster/jobs` keeps finished jobs about 300 s). Record-based POSTs also return a `results` link (`?job_results_uuid=<uuid>`). |
| Errors | Body `{"error": {"message": ..., "code": ..., "target": ...}}`. Multi-record jobs report `errors` and `rollback_errors`. **429** / **503** = too many requests: retry after a delay (`Retry-After`). |

## 2. Dangerous behaviours to respect (from NetApp's docs)
- **Query-based PATCH and DELETE.** `PATCH` or `DELETE` on a **collection** with a query (e.g. `PATCH /api/storage/volumes?name=simpson` with `{"state": "offline"}`) applies to **every matching record**. It runs for `return_timeout` seconds (15 by default), then returns a `next` link to continue with the same method. One wrong query can take many volumes offline or delete them. **This skill forbids query-based PATCH/DELETE on production.** Always act on one record by its UUID (`/api/storage/volumes/<uuid>`).
- `max_records` also limits how many records a query-based PATCH/DELETE acts on. It's not a safety net: don't rely on it.
- **Rollback:** POST and PATCH try to roll back earlier records when a later one fails (unless `continue_on_failure=true`). **DELETE never rolls back** and always behaves as `continue_on_failure`.
- `serial_records=true` forces records to be processed in order. Parallel is the default.
- `/api/private/cli/...` passes CLI commands through REST, with the same RBAC. Every such call is a CLI command: it needs a `[doc]` source for the CLI form (ontap-command-catalog.md) like any other.
- A `202` doesn't mean success. Wait for the job, and read back the object.

## 3. ASA r2 differences (NetApp's *REST API support for ASA r2*)
- The ASA r2 API is based on the unified ONTAP API, with changes: new endpoints (storage units under `/api/storage/storage-units`, which aggregate LUNs and NVMe namespaces; also see `/api/storage/luns` and `/api/storage/namespaces`), methods that aren't allowed (e.g. no POST/DELETE on `/api/protocols/nvme/services`), properties that aren't supported (e.g. PATCH `/api/storage/volumes/{uuid}` doesn't take `autosize.maximum`, `autosize.minimum`, `autosize.mode`), and different processing (e.g. DELETE `/api/storage/luns/{uuid}` is asynchronous).
- In the system's Swagger UI, search for **Platform Specifics** to see ASA r2 support per call and property.
- The committed catalog is unified ONTAP 9.16. For ASA r2, everything is `[unverified]` until checked against the system's own reference (`../asa-api-local/`).

## 4. Reference client (requests only)
```python
"""Minimal ONTAP REST client. Read-only by default; writes need allow_writes=True and act on one UUID at a time."""
import os
import time
import requests

class Ontap:
    def __init__(self, host, user, password, ca_bundle=True, allow_writes=False, timeout=30):
        self.base = f"https://{host}"
        self.allow_writes = allow_writes          # keep False for audits/monitoring
        self.timeout = timeout
        self.s = requests.Session()
        self.s.auth = (user, password)            # use a read-only role for reporting code
        self.s.verify = ca_bundle                 # path to CA bundle; never False in production
        self.s.headers["Accept"] = "application/json"

    def _req(self, method, path, params=None, json=None):
        if method != "GET":
            if not self.allow_writes:
                raise PermissionError(f"write blocked ({method} {path}): client is read-only")
            if method in ("PATCH", "DELETE") and params:
                raise PermissionError("query-based PATCH/DELETE is forbidden: address one record by UUID")
        r = self.s.request(method, f"{self.base}{path}", params=params, json=json, timeout=self.timeout)
        body = r.json() if r.content else {}
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {body.get('error')}")
        if r.status_code == 202 and "job" in body:
            self.wait_job(body["job"]["uuid"])
        return body

    def get_all(self, path, fields=None, **query):
        """Iterate every record of a collection, following _links.next."""
        params = dict(query, max_records=500)
        if fields:
            params["fields"] = ",".join(fields)
        url = path
        while url:
            body = self._req("GET", url, params=params)
            yield from body.get("records", [])
            url = body.get("_links", {}).get("next", {}).get("href")
            params = None                           # the next href already holds the query

    def wait_job(self, uuid, poll=2, limit=600):
        end = time.time() + limit
        while time.time() < end:
            job = self._req("GET", f"/api/cluster/jobs/{uuid}", params={"fields": "state,message,code,error"})
            if job["state"] in ("success", "failure"):
                if job["state"] == "failure":
                    raise RuntimeError(f"job {uuid} failed: {job.get('code')} {job.get('message')}")
                return job
            time.sleep(poll)
        raise TimeoutError(f"job {uuid} still running after {limit}s: check it before doing anything else")

# --- read-only example (T0) ---
if __name__ == "__main__":
    c = Ontap(os.environ["ONTAP_HOST"], os.environ["ONTAP_USER"], os.environ["ONTAP_PASSWORD"],
              ca_bundle=os.environ.get("ONTAP_CA", True))
    for n in c.get_all("/api/cluster/nodes", fields=["name", "version"]):
        print(n["name"], n["version"]["full"])
    for v in c.get_all("/api/storage/volumes", fields=["name", "uuid", "svm.name", "state", "size"]):
        print(v["svm"]["name"], v["name"], v["state"], v["size"])
```
Names used: `/cluster/nodes` filters `version.full`, `/storage/volumes` fields `name`, `uuid`, `state`, `size` and filter `svm.name`, and `/cluster/jobs` fields `state`, `message`, `code`, `error` (all in areas/). Job states `success` / `failure` are from the catalog's `/cluster/jobs` description.

## 5. Safety rules for code that touches clusters
1. **Read-only role by default** for monitoring and reporting (`allow_writes=False`). Write-capable credentials live in a vault and are used only by approved change automation.
2. **Secrets:** read credentials from environment variables or a vault. Never hard-code, print or log them. Never commit them.
3. **TLS:** verify certificates (`verify=<CA bundle>`). `verify=False` is never acceptable against production.
4. **No query-based PATCH/DELETE.** Resolve the exact UUID with a GET, show it, then act on `/api/.../<uuid>` only.
5. **Writes go through the change gate.** The code produces a plan (exact method, path, UUID and body) for human approval, or runs only approved steps. One object per call for T2/T3, wait for the job, read back, stop at the first error.
6. **Dry-run first:** for any write function, implement `--dry-run` that prints the method, path and body without sending.
7. **Version-aware:** read `version` from `/api/cluster/nodes` at start-up. Don't use a field whose *since* is newer than the cluster. Use `ignore_unknown_fields=true` only for reads.
8. **Test against a non-production cluster first** (or ONTAP Select / a simulator if your site has one).
9. **Rate and load:** `max_records` in the hundreds, back off on 429/503, and don't poll metrics faster than needed.
