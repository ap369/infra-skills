#!/usr/bin/env python3
"""Generate a Markdown API reference from an OpenAPI 3.x or Swagger 2.0 spec.

Usage (from repo root, needs PyYAML):
    python3 scripts/gen_api_docs.py <profile> <path/to/spec.yaml|json>

Profiles (output folder in brackets; *-api-local/ folders are git-ignored and must never be committed):
    flashblade  [managing-purestorage-production/references/flashblade-api]      Apache-2.0 spec, committed
    flasharray  [managing-purestorage-production/references/flasharray-api]      Apache-2.0 spec, committed
    ontap       [managing-netapp-production/references/ontap-api-local]          cluster's /docs/api/swagger.yaml, local only
    asa         [managing-netapp-production/references/asa-api-local]            ASA r2 system's swagger, local only
    powermax    [managing-powermax-production/references/powermax-api-local]     Dell Unisphere OpenAPI, local only
    unity       [managing-unity-vnx-production/references/unity-api-local]       Unity OpenAPI, local only

Writes into the output folder:
    endpoints.md          index of every operation (method, path, summary, risk tier)
    areas/<area>.md       full detail per API area (tag): parameters, body, responses
    models.md             every schema with its properties
    spec/<spec file>      the spec itself (copied, unmodified)
README.md, python-dev-guide.md and NOTICE.md are hand-written and not overwritten.
"""
import json
import pathlib
import re
import shutil
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
METHODS = ("get", "post", "put", "patch", "delete")

PURE_NOTE = ("> Source: Pure Storage / Everpure official OpenAPI spec, **{title} {version}**, from "
             "github.com/purestorage-openconnect/swagger (Apache-2.0, see NOTICE.md). Everything here is `[doc]` "
             "for **this API version**. Check the array's supported versions with `GET /api/api_version` and use "
             "the highest version both sides support.\n")
LOCAL_NOTE = ("> **LOCAL ONLY: do not commit or share.** Generated from {source}, **{title} {version}**. "
              "The spec is the vendor's copyrighted material. Everything here is `[doc]` for **this API version**{extra}. "
              "Check the target's version with `{check}` first.\n")

PROFILES = {
    "flashblade": dict(out="managing-purestorage-production/references/flashblade-api", name="FlashBlade REST API",
                       note=PURE_NOTE),
    "flasharray": dict(out="managing-purestorage-production/references/flasharray-api", name="FlashArray REST API",
                       note=PURE_NOTE),
    "ontap": dict(out="managing-netapp-production/references/ontap-api-local", name="ONTAP REST API",
                  note=LOCAL_NOTE, source="the cluster's own spec (`https://<cluster-mgmt>/docs/api/swagger.yaml`)",
                  check="GET /api/cluster/nodes?fields=version", extra=""),
    "asa": dict(out="managing-netapp-production/references/asa-api-local", name="ASA r2 (ONTAP) REST API",
                note=LOCAL_NOTE, source="the ASA r2 system's own spec (`https://<cluster-mgmt>/docs/api/swagger.yaml`)",
                check="GET /api/cluster/nodes?fields=version", extra=""),
    "powermax": dict(out="managing-powermax-production/references/powermax-api-local", name="Unisphere for PowerMax REST API",
                     note=LOCAL_NOTE, source="Dell's Unisphere for PowerMax OpenAPI spec",
                     check="GET /univmax/restapi/version", extra=""),
    "unity": dict(out="managing-unity-vnx-production/references/unity-api-local", name="Unity Unisphere Management REST API",
                  note=LOCAL_NOTE, source="a Unity OpenAPI spec (see README.md for provenance)",
                  check="GET /api/types/basicSystemInfo/instances",
                  extra=" **as far as the source spec is accurate**: if it's a community conversion, confirm a path or "
                        "attribute in the system's own `https://<unity>/apidocs/` before using it in a change"),
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def short(text, n=220):
    t = re.sub(r"</?(p|b|i|a|br|li|ul|ol|em|strong|hr|div|span|tt)\b[^>]*>", " ", text or "")
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("|", "\\|")
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def ref_name(ref):
    return ref.rsplit("/", 1)[-1]


def resolve(spec, obj):
    seen = 0
    while isinstance(obj, dict) and "$ref" in obj and seen < 10:
        parts = obj["$ref"].lstrip("#/").split("/")
        node = spec
        for p in parts:
            node = node[p]
        obj = node
        seen += 1
    return obj


def type_of(spec, schema):
    if not isinstance(schema, dict):
        return ""
    if "$ref" in schema:
        return f"`{ref_name(schema['$ref'])}`"
    if "allOf" in schema:
        return " + ".join(type_of(spec, s) for s in schema["allOf"])
    t = schema.get("type", "object")
    if t == "array":
        return f"array of {type_of(spec, schema.get('items', {}))}"
    extra = []
    if schema.get("format"):
        extra.append(schema["format"])
    if schema.get("enum"):
        extra.append("enum: " + ", ".join(f"`{e}`" for e in schema["enum"][:12]))
    return t + (f" ({'; '.join(extra)})" if extra else "")


def props(spec, schema, depth=0):
    """Flatten properties of a schema (following allOf and $ref) one level deep."""
    schema = resolve(spec, schema)
    out = {}
    if not isinstance(schema, dict):
        return out
    for part in schema.get("allOf", []):
        out.update(props(spec, part, depth + 1))
    for name, p in (schema.get("properties") or {}).items():
        out[name] = p
    return out


def tier(method, path, op):
    m = method.lower()
    if m == "get":
        return "T0"
    if m == "delete":
        return "T3"
    if path.endswith(("/login", "/logout")) or "oauth2" in path or "token" in path:
        return "auth"
    if m in ("patch", "put"):
        return "T2 (T3 if it destroys, eradicates, disables or overwrites)"
    if "/action/" in path:
        return "T1–T3 (action: read its description)"
    return "T1+ (check: some POSTs are actions)"


def schema_of_content(content):
    if not content:
        return None
    for mt in ("application/json", "application/hal+json", "*/*"):
        if mt in content:
            return content[mt].get("schema")
    return next(iter(content.values())).get("schema")


def normalize_swagger2(spec):
    """Rewrite Swagger 2.0 body params, param types and response schemas into the OpenAPI 3 shape used below."""
    if not str(spec.get("swagger", "")).startswith("2"):
        return

    def fix_params(params):
        body, kept = None, []
        for p in params:
            p = resolve(spec, p)
            if p.get("in") == "body":
                body = {"required": p.get("required", False), "content": {"application/json": {"schema": p.get("schema", {})}}}
                continue
            if "schema" not in p:
                p["schema"] = {k: p[k] for k in ("type", "format", "enum", "items") if k in p}
            kept.append(p)
        return body, kept

    for item in spec.get("paths", {}).values():
        _, item["parameters"] = fix_params(item.get("parameters", []))
        for m in METHODS:
            op = item.get(m)
            if not op:
                continue
            body, op["parameters"] = fix_params(op.get("parameters", []))
            if body and "requestBody" not in op:
                op["requestBody"] = body
            for r in (op.get("responses") or {}).values():
                r = resolve(spec, r)
                if "schema" in r and "content" not in r:
                    r["content"] = {"application/json": {"schema": r["schema"]}}


def load(src):
    raw = src.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp1252", errors="replace")
    return json.loads(text) if src.suffix == ".json" else yaml.safe_load(text)


def field_rows(spec, fields):
    rows = ["| Field | Type | Description |", "|---|---|---|"]
    for fname, fp in fields.items():
        fpr = resolve(spec, fp) if isinstance(fp, dict) and "$ref" in fp else fp
        ro = " (read-only)" if isinstance(fpr, dict) and fpr.get("readOnly") else ""
        rows.append(f"| `{fname}` | {type_of(spec, fp)}{ro} | {short((fpr or {}).get('description') if isinstance(fpr, dict) else '')} |")
    return rows + [""]


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in PROFILES:
        sys.exit(__doc__)
    prof = PROFILES[sys.argv[1]]
    out = ROOT / prof["out"]
    src = pathlib.Path(sys.argv[2])
    spec = load(src)
    normalize_swagger2(spec)
    version = spec["info"].get("version", "?")
    title = re.sub(r"\s+", " ", spec["info"].get("title", prof["name"])).strip()
    (out / "areas").mkdir(parents=True, exist_ok=True)
    (out / "spec").mkdir(parents=True, exist_ok=True)
    for old in (out / "areas").glob("*.md"):
        old.unlink()
    if src.resolve() != (out / "spec" / src.name).resolve():
        shutil.copy(src, out / "spec" / src.name)

    by_tag = {}
    for path, item in spec["paths"].items():
        common = item.get("parameters", [])
        for m in METHODS:
            if m not in item:
                continue
            op = item[m]
            for t in op.get("tags", ["Other"]):
                by_tag.setdefault(t, []).append((path, m, op, common))

    header = (f"<!-- GENERATED by scripts/gen_api_docs.py from {src.name} "
              f"({title} {version}). Do not edit by hand; regenerate. -->\n")
    note = prof["note"].format(title=title, version=version, source=prof.get("source", ""),
                               check=prof.get("check", ""), extra=prof.get("extra", ""))

    # endpoints index
    total = sum(len(v) for v in by_tag.values())
    lines = [header, f"# {prof['name']} {version}: endpoint index", "", note,
             f"{len(spec['paths'])} paths, {total} operations, {len(by_tag)} areas. "
             "The tier is this skill's risk tier: anything other than T0 goes through change-gate.md.", ""]
    for t in sorted(by_tag):
        lines += [f"## [{t}](areas/{slug(t)}.md)", "", "| Method | Path | Summary | Tier |", "|---|---|---|---|"]
        for path, m, op, _ in sorted(by_tag[t], key=lambda x: (x[0], METHODS.index(x[1]))):
            lines.append(f"| {m.upper()} | `{path}` | {short(op.get('summary') or op.get('description'), 90)} | {tier(m, path, op)} |")
        lines.append("")
    (out / "endpoints.md").write_text("\n".join(lines))

    # per-area detail
    for t, ops in by_tag.items():
        L = [header, f"# {t} ({title} {version})", "", note, f"[← endpoint index](../endpoints.md)", ""]
        for path, m, op, common in sorted(ops, key=lambda x: (x[0], METHODS.index(x[1]))):
            L += [f"## {m.upper()} `{path}`", "", f"**Tier:** {tier(m, path, op)}  ", ""]
            if op.get("description"):
                L += [short(op["description"], 600), ""]
            params = [resolve(spec, p) for p in common + op.get("parameters", [])]
            unnamed = [p for p in params if not p.get("name")]
            params = [p for p in params if p.get("name")]
            if params:
                L += ["| Parameter | In | Type | Required | Description |", "|---|---|---|---|---|"]
                for p in params:
                    L.append(f"| `{p.get('name')}` | {p.get('in')} | {type_of(spec, p.get('schema', {}))} | "
                             f"{'yes' if p.get('required') else ''} | {short(p.get('description'))} |")
                L.append("")
            if unnamed:
                L += [f"_{len(unnamed)} parameter(s) have no name in the source spec and are omitted._", ""]
            body = op.get("requestBody")
            if body:
                body = resolve(spec, body)
                bs = schema_of_content(body.get("content"))
                name = ref_name(bs["$ref"]) if isinstance(bs, dict) and "$ref" in bs else "inline"
                L += [f"**Request body** ({'required' if body.get('required') else 'optional'}): `{name}`", ""]
                bp = props(spec, bs) if bs else {}
                if bp:
                    L += field_rows(spec, bp)
            resp = []
            for code, r in (op.get("responses") or {}).items():
                r = resolve(spec, r)
                rs = schema_of_content(r.get("content"))
                rn = ref_name(rs["$ref"]) if isinstance(rs, dict) and "$ref" in rs else ""
                hdrs = [h for h in (r.get("headers") or {}) if h.lower() != "x-request-id"]
                inline = ""
                if isinstance(rs, dict) and "$ref" not in rs and rs.get("properties"):
                    inline = " body fields: " + ", ".join(f"`{k}`" for k in rs["properties"])
                resp.append(f"`{code}` {short(r.get('description'), 60)}" + (f" → `{rn}`" if rn else "")
                            + (" · headers: " + ", ".join(f"`{h}`" for h in hdrs) if hdrs else "") + inline)
            if resp:
                L += ["**Responses:** " + " · ".join(resp), ""]
        (out / "areas" / f"{slug(t)}.md").write_text("\n".join(L))

    # models
    schemas = (spec.get("components") or {}).get("schemas") or spec.get("definitions") or {}
    M = [header, f"# {prof['name']} {version}: models", "", note,
         f"{len(schemas)} schemas. A field marked read-only is returned by the system, never sent.", ""]
    for name in sorted(schemas):
        s = schemas[name]
        M += [f"## `{name}`", ""]
        if isinstance(s, dict) and s.get("description"):
            M += [short(s["description"], 400), ""]
        ps = props(spec, s)
        if ps:
            M += field_rows(spec, ps)
        elif isinstance(s, dict) and s.get("allOf"):
            M += ["Composition: " + type_of(spec, s), ""]
        elif isinstance(s, dict):
            M += ["Type: " + type_of(spec, s), ""]
    (out / "models.md").write_text("\n".join(M))
    print(f"{title} {version}: {total} operations, {len(by_tag)} areas, {len(schemas)} models -> {out}")


if __name__ == "__main__":
    main()
