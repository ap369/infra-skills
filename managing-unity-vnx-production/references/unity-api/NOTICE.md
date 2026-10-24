# Notice

`spec/unity_openapi.json` is an OpenAPI conversion of the *Unisphere Management REST API Reference Guide* 5.4.0,
copied unmodified from https://github.com/sachdev27/dell-unity-mcp-server (file `openapi.json`, retrieved 2026-10-25).
That repository is under the **MIT License** ("Copyright (c) 2024 Dell Technologies"); a copy is in `spec/LICENSE`.

It is **not an official Dell publication**: it is a community conversion, and some content (e.g. query-parameter
names) was lost. The underlying reference text is Dell's.

`endpoints.md`, `areas/*.md` and `models.md` are derived works, generated mechanically from that file by
`scripts/gen_api_docs.py` (profile `unity`) in this repository. The system's own API reference
(`https://<unity-mgmt>/apidocs/`) and Dell's official documentation are authoritative.

Dell and Unity are trademarks of Dell Inc. or its subsidiaries. This repository isn't affiliated with or endorsed by Dell.
