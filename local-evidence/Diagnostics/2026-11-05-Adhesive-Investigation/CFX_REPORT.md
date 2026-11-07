# Official Adhesive DLL fails PROCESS_ATTACH under CachyOS Wine 11.0

Prepared locally on 2026-11-05. This report has not been submitted. Scope is offline initialization compatibility only; no protected/public server connections or authentication experiments were performed.

## Observed failure

The historical FiveM launcher log explicitly records Adhesive load failure with Win32 error 998 and then Sticky fallback. A separate offline, CoreRT-first, unmodified Windows loader probe reproduces error 998, with an access violation during Adhesive PROCESS_ATTACH:

```
Exception: 0xC0000005, memory read
Instruction RVA: adhesive.dll + 0xD9FEC5
Adhesive chain: +0xD9FEC5 -> +0xD9DE92 -> +0xD9DDC9 -> +0xD9DC96 -> +0xCC2457
Caller: UCRT _initterm, then Adhesive CRT startup
VirtualQuery(read target).State: MEM_FREE (0x10000)
LoadLibraryExW result: NULL
GetLastError: 998
```

Different process layouts change module bases and invalid target addresses; the instruction RVA remains identical in all five runs. The VEH logger always returns EXCEPTION_CONTINUE_SEARCH. No instruction, exception context, memory mapping, import result, security condition or Wine identity is patched.

## Exact files and environment

- Adhesive size: 54,552,672 bytes; SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`. Matches the existing local official-reference copy named adhesive-24769.dll. Embedded signer subject: Rockstar Games, Inc. Signed-content signature and PE SHA256 digest check pass; CA trust/revocation and original download provenance were not revalidated.
- Source branch baseline: PR4050 head `ba07d9d3d5bd8459b69a81c69eb6065d4e11273c`, with preexisting local ordinary compatibility changes; snapshot preserved in existing-source-before.patch. No new FiveM source patch was made in this investigation.
- Old CoreRT SHA256: `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013`.
- Rebuilt CoreRT SHA256: `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64`.
- Wine `wine-11.0 (CachyOS)`, Proton `cachyos-11.0-20261015-slr`, Heroic Flatpak v2.22.4, runtime26.08.
- Ubuntu on PS5 hardware, AMD Zen2/RADV GFX1013 as reported by the owner; loader tests do not initialize GTA or validate graphics.
- Reused account-free diagnostic prefix; networking disabled by Flatpak; original client directories granted read-only access.

## Controls actually executed

1. Old CoreRT + built-in Wine C/C++ runtime: fault +0xD9FEC5, read0xA5D1CA, error998.
2. New CoreRT + built-in runtime: same fault, read0xA5BEFA, error998.
3. New CoreRT + native Microsoft MSVCP140/VCRUNTIME140/VCRUNTIME140_1 14.44.35211.0: same fault, read0xA4D50A, error998.
4. Restored built-in runtime repeat: same fault, read0xA5BEFA, error998.
5. Native VC++ set plus native UCRT10.0.10586.15: same fault, read0xA4FB1A, error998. Native _initterm frame moves to UCRT RVA0x51AF, consistent with a different CRT implementation calling the same failing initializer.

Each CoreRT preload succeeds with zero observed exceptions, and its resolved path is logged. Wine MSVCP140 lacks eight imported money-facet locale-ID data exports used by CoreRT. Control3 supplies all eight and removes those import warnings, without fixing the failure. This excludes merely supplying these exports as a sufficient fix; it does not certify all runtime APIs.

Microsoft runtime files were already present on the owner's device, copied only into the diagnostic prefix temporarily, and restored byte-for-byte. Their signed-content signatures and PE SHA256 digests match; trust chain/revocation were not independently verified.

## Reproducer and evidence

The accompanying CRT-free x64 probe uses normal LoadLibraryExW(LOAD_WITH_ALTERED_SEARCH_PATH), preloads CoreRT ordinary globals, then loads the same Adhesive DLL. It never calls EarlyMode_Init, WineCompat_InstallHooks, CreateComponent or any connection path. Its imports are Kernel32 only. It logs first-chance exceptions and memory-region metadata without consuming exceptions.

Build: `bash build-loader-probe.sh`. Run from this directory: `python3 run-probe.py new --tag unique-tag`. Full absolute command examples, native-runtime control, exact file hashes, and restoration details are in REPORT_AR.md. Run sequentially; result code10 means the probe observed a DLL-load failure. Paths are fixed to the owner's local project and must be reviewed/adapted for an approved developer harness.

Shareable local artifacts: loader-probe.c, build-loader-probe.sh, loader-probe-kernel32.def, loader-probe-v3-v4.diff, results.json and trace-excerpts.txt. Raw logs/dumps remain local and should be reviewed before any sharing. Do not distribute proprietary DLLs or private prefix data with this report.

## Limits and requested developer diagnosis

The standalone host does not reproduce the full FiveM launcher context. No historical dump contains Adhesive mapped, and the historical actual-client error998 log lacks a first-fault stack. We have **not** proven that this isolated fault RVA is the same cause as the historical full-client failure. The current Run-CoreRT-Test directory has no adhesive.dll and its Sticky log is not an Adhesive test.

Please identify the initializer at these RVAs for the given DLL hash, specify its required host initialization and the origin of its invalid read pointer, and advise an approved offline diagnostic configuration or symbols to reproduce this in the real host. If a public Windows API behaves incorrectly, an independent API reproducer and Wine-compatible patch can follow. No unsupported-platform check is assumed or requested to be disabled. No protection-policy changes, authentication modifications or identity masking are proposed.

Current status: reproducible initialization failure; no confirmed public-API root cause, no operational fix, no proof of security functionality or official Wine support.
