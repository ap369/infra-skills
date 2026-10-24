# Notice

`spec/openapi.json` is Dell's Unisphere for PowerMax OpenAPI specification (title "PowerMax 10.3"), copied unmodified
from https://github.com/dell/PyU4V (file `PyU4V/tools/openapi.json`, retrieved 2026-10-25).

That repository is published by Dell Technologies under the **Apache License, Version 2.0**. A copy of the license is in
`spec/LICENSE`. Copyright belongs to Dell Inc. or its subsidiaries.

`endpoints.md`, `areas/*.md` and `models.md` are derived works, generated mechanically from that specification by
`scripts/gen_api_docs.py` (profile `powermax`) in this repository. Descriptions are abbreviated. When in doubt, the
REST documentation served by your Unisphere (`https://<unisphere>:8443/univmax/restapi/docs`) and Dell's official
documentation are authoritative.

Dell, PowerMax, VMAX and Unisphere are trademarks of Dell Inc. or its subsidiaries. This repository isn't affiliated
with or endorsed by Dell.
