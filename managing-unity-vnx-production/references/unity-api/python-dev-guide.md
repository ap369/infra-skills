# Python development against the Unity REST API (plain HTTP, no SDK)

Sources: the text of Dell's *Unisphere Management REST API Reference Guide* **5.4.0** as carried in the community `openapi.json` (README.md, *Provenance*; generated lookup files in [endpoints.md](endpoints.md), [areas/](areas/), [models.md](models.md)), and Dell's KB on using cURL with the Unity REST API (headers, CSRF). Retrieved 2026-10-25. **Confirm every resource, action and attribute in `https://<unity-mgmt>/apidocs/` before using it in a change.** If you can't, it's `[unverified]` (command-verification.md).

## 1. Basics
| Topic | Fact |
|---|---|
| Base URL | `https://<unity-mgmt>` |
| Collections | `GET /api/types/<resourceType>/instances` (e.g. `/api/types/lun/instances`) |
| One instance | `GET /api/instances/<resourceType>/<id>` or `/api/instances/<resourceType>/name:<name>` |
| Create / class actions | `POST /api/types/<resourceType>/action/<action>` (e.g. `/api/types/storageResource/action/createLun`) |
| Instance actions | `POST /api/instances/<resourceType>/<id>/action/<action>` (e.g. `.../storageResource/<id>/action/modifyLun`). **Modify is a POST action, not PATCH.** |
| Delete | `DELETE /api/instances/<resourceType>/<id>` (e.g. `storageResource`) |
| Auth | HTTP Basic. Header **`X-EMC-REST-CLIENT: true`** is "required to send in all requests if using Basic authentication". Keep the session cookies (use one `requests.Session`). |
| CSRF | Header **`EMC-CSRF-TOKEN`**: "gathered from a GET response and required to send with POST and DELETE requests. It is good for the entirety of the session." |
| Logout | `POST /api/types/loginSessionInfo/action/logout` |
| Unauthenticated info | `GET /api/types/basicSystemInfo/instances`: model, system name, software version, API version |
| Query options seen in the reference text | `fields=a,b` (attributes to return), `filter=<attr> eq <value>` (e.g. `filter=queryId eq 37`), `compact=true`, `per_page=<n>` |
| Collection response | `@base`, `updated`, `links` (`rel`: `self`, `first`, `prev`, `next`, `last`; `href` is appended to `@base`), `entryCount`, `entries[]` (each with `content`) |
| Async | Long operations can run as jobs (`GET /api/types/job/instances`). The storageResource delete text warns: "If this method is called asynchronously then the storage resource may still exist after the call." Read back after every change. |

## 2. Destructive actions to respect
- `DELETE /api/instances/storageResource/<id>` deletes a LUN, consistency group, file system or datastore **with its data** (T3).
- `POST .../storageResource/<id>/action/refresh` (and snapshot restore actions) overwrite the resource's data with a snapshot or source: T3.
- `modifyLun` / `modifyFilesystem` / `modify...` actions can shrink, change host access or remove hosts. Tier the **attributes you send**: removing host access = T3; shrinking = T3.
- The generated files tier every `/action/` POST as "T1–T3 (action: read its description)". Decide the tier from the action and body, and say why in the plan.

## 3. Reference client (requests only)
```python
"""Minimal Unity REST client. Read-only by default; writes need allow_writes=True."""
import os
import requests

class Unity:
    def __init__(self, host, user, password, ca_bundle=True, allow_writes=False, timeout=60):
        self.base = f"https://{host}"
        self.allow_writes = allow_writes          # keep False for audits/monitoring
        self.timeout = timeout
        self.s = requests.Session()
        self.s.auth = (user, password)            # Operator/read-only role for reporting code
        self.s.verify = ca_bundle                 # path to CA bundle; never False in production
        self.s.headers.update({"X-EMC-REST-CLIENT": "true", "Accept": "application/json",
                               "Content-Type": "application/json"})
        info = self.get("/api/types/basicSystemInfo/instances")      # also captures the CSRF token
        self.info = info["entries"][0]["content"] if info.get("entries") else {}

    def _req(self, method, path, params=None, json=None):
        if method != "GET" and not self.allow_writes:
            raise PermissionError(f"write blocked ({method} {path}): client is read-only")
        url = path if path.startswith("https://") else f"{self.base}{path}"
        r = self.s.request(method, url, params=params, json=json, timeout=self.timeout)
        token = r.headers.get("EMC-CSRF-TOKEN")
        if token:
            self.s.headers["EMC-CSRF-TOKEN"] = token                  # never log this value
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
        return r.json() if r.content else {}

    def get(self, path, **params):
        return self._req("GET", path, params=params or None)

    def instances(self, rtype, fields, **params):
        """Yield every instance's content, following the 'next' link."""
        body = self.get(f"/api/types/{rtype}/instances", fields=",".join(fields), **params)
        while True:
            for e in body.get("entries", []):
                yield e.get("content", {})
            nxt = next((l["href"] for l in body.get("links", []) if l.get("rel") == "next"), None)
            if not nxt:
                return
            body = self._req("GET", body["@base"] + nxt)              # absolute URL from the response

    def logout(self):
        if "EMC-CSRF-TOKEN" in self.s.headers:
            self.s.post(f"{self.base}/api/types/loginSessionInfo/action/logout", timeout=self.timeout)

# --- read-only example (T0) ---
if __name__ == "__main__":
    u = Unity(os.environ["UNITY_HOST"], os.environ["UNITY_USER"], os.environ["UNITY_PASSWORD"],
              ca_bundle=os.environ.get("UNITY_CA", True))
    try:
        print(u.info)
        for lun in u.instances("lun", ["id", "name", "sizeTotal"]):
            print(lun)
    finally:
        u.logout()
```
**Confirm in `/apidocs/` before use:** the attribute names `id`, `name`, `sizeTotal` for `lun`, and how `next` links combine with `@base` on your OE version (read one paged response on a non-production system). The headers, URL patterns and logout path are from the reference text above.

## 4. Safety rules for code that touches arrays
1. **Read-only role by default** for reporting code (`allow_writes=False`). Write-capable credentials live in a vault and are used only by approved change automation.
2. **Secrets:** read credentials from environment variables or a vault. Never hard-code, print or log them (password, `EMC-CSRF-TOKEN`, session cookies). Never commit them.
3. **TLS:** verify certificates (`verify=<CA bundle>`). `verify=False` is never acceptable against production.
4. **Writes go through the change gate.** The code produces a plan (exact method, path, `id` and body) for human approval, or runs only approved steps. Address objects by `id` (resolved by a GET and shown to the human). One object per call for T2/T3, read back after each, stop at the first error.
5. **Dry-run first:** for any write function, implement `--dry-run` that prints the method, path and body without sending.
6. **Test against a non-production system first** (UnityVSA is a good target). Check `basicSystemInfo` at start-up and pin the OE version you tested against.
7. **Rate and load:** use `fields=` to fetch only what you need, page with `per_page` in the hundreds, and don't poll metrics faster than needed.
