# Local artifact inventory (not automatically uploaded)

Root on the original PS5 Ubuntu installation:
`/home/feras/Projects/FiveM-PR4050-Test`

The repository can preserve **only accessible, reviewed content**. This inventory records original paths reported in the Codex session logs. The actual files may be absent from GitHub until imported from the user's own machine.

## Source and runtime

| Original path | Purpose | Publish? |
| --- | --- | --- |
| `Original-PR4050-Source/` | Forked FiveM source + local edits | **Diffs only**; link upstream for original content |
| `PR-4050.patch` | Community proposal patch snapshot | Text; check origin/license |
| `Compiled-Release/` | Large precompiled client | **No** |
| `Run-Test/` | Working client runtime | **No** |
| `Run-Adhesive-Test/` | Official DLL and runtime test | **No binaries/logs** |
| `Run-CoreRT-Test/` | Targeted CoreRT build runtime | **No binaries/logs** |
| `Official-Reference/adhesive-24769.dll` | Official proprietary security DLL | **Never redistribute** |
| `Wine-Test-Prefix/` | Wine prefix with user state | **No** |

## Diagnostics

| Original path | Recorded role |
| --- | --- |
| `Diagnostics/2026-11-04/` | Earlier CoreRT/Wine compatibility experiment |
| `Diagnostics/2026-11-05-Compatibility/` | Source fixes, validation, compatibility probes |
| `Diagnostics/2026-11-05-Adhesive-Phase2/` | Original Adhesive initialization/fault checks |
| `Diagnostics/2026-11-05-Adhesive-Resolver-Probe/` | NTDLL export lookup diagnostics |
| `Diagnostics/2026-11-05-Adhesive-RCA/` | Index origin and root-cause investigation |
| `Diagnostics/2026-11-05-Adhesive-Direct-Repair/` | Compatibility investigation snapshots |
| `Diagnostics/2026-11-07-TLS-Causality/` | Controlled TLS test and unsuccessful prototype |
| `Diagnostics/2026-11-07-Export-Bounds/` | Final resolver-bound tests and findings |

Directories shown are from recorded session references; verify existence before importing. Prefer Markdown, source code and `.patch` files **outside any `private/` subtree**, with manual secret review.

## Preserve locally, do not publish by default

`*.dmp`, `*.dll`, `*.exe`, `*.pdb`, `*.pak`, `*.vmdk`, `*.qcow2`, Wine prefixes, personal data, credentials, authentication tickets, private reports with raw memory, `*.log` and copyrighted game assets.

The raw multi-megabyte Codex chat exports are **not** published verbatim because they may contain sensitive environment details and copied code from third parties. This curated research archive captures the documented engineering findings.

## Integrity values (historical, not rehashed)

Official Adhesive reference SHA256: `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`

Targeted CoreRT SHA256: `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64`
