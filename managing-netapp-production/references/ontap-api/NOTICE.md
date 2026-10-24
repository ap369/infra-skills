# Notice

`spec/ontap_api_catalog.json` is the ONTAP REST API catalog (ONTAP 9.16, generated 2026-03-26) from NetApp's
**ontap-mcp** project, copied unmodified from https://github.com/NetApp/ontap-mcp (file `conf/ontap_api_catalog.json`,
retrieved 2026-10-25).

That repository is licensed under the **Apache License, Version 2.0**. A copy of the license is in `spec/LICENSE`.
Copyright belongs to NetApp, Inc. and its contributors.

`endpoints.md` and `areas/*.md` are derived works, generated mechanically from that catalog by
`scripts/gen_ontap_catalog_docs.py` in this repository. Descriptions are abbreviated. When in doubt, NetApp's official
ONTAP REST API documentation (docs.netapp.com, and `https://<cluster-mgmt>/docs/api` on the system) is authoritative.

The full ONTAP / ASA r2 API reference (swagger) is NetApp copyrighted material: it is **not** included in this
repository. Generate it locally from your own cluster (README.md); the output folders `*-api-local/` are git-ignored.

NetApp and ONTAP are trademarks of NetApp, Inc. This repository isn't affiliated with or endorsed by NetApp.
