# Adhesive evidence audit — 2026-11-05

Read-only inspection of existing runtime artifacts. Only this report and `minidump-summary.json` were created by this audit; no executable, source, runtime DLL or prefix was changed.

## Existing measured failure

`Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log:3` explicitly records Adhesive load failure 998 followed by Sticky fallback. `Run-CoreRT-Test/logs/CitizenFX_log_2026-11-05T124119.log:166` records Sticky at pre-gameload only; it does not demonstrate an Adhesive load attempt.

The earlier standalone v3 test first loaded ordinary CoreRT globals successfully, with no observed CoreRT exceptions, then loaded official Adhesive using `LoadLibraryExW(LOAD_WITH_ALTERED_SEARCH_PATH)`. Its result file records Adhesive handle zero, error998, one loader exception and probe exit10. Evidence: `../2026-11-05-Compatibility/standalone-adhesive-initialized-result.txt:4-13`.

Full private trace `../2026-11-05-Compatibility/private/api-probe-cachyos/adhesive-initialized-v3.log:15965` enters Adhesive PROCESS_ATTACH; lines16014-16021 record a read access violation `0xC0000005` at `adhesive+0xD9FEC5`, target `0xA5D36A`; lines16050-16053 record failed initialization. The logger returns CONTINUE_SEARCH, preserving normal exception handling. The sanitized trace excerpt is `../2026-11-05-Compatibility/standalone-adhesive-initialized-excerpt.txt`.

Only the single faulting instruction was inspected: `movzbl (%r9,%rax,1),%esi`. Recorded `r9=0x7AD340`, `rax=0x2B002A` give the target `0xA5D36A`. The stack contains `_initterm+0x2A` based on the previously checked actual UCRT export metadata; it supports static initialization within CRT/DllMain, rather than identifying a TLS callback or specific unsupported API.

The standalone process does not reproduce all FiveM launcher context. Its failure RVA is not yet conclusively linked to the historical real-client error998. No trace establishes intentional platform refusal, driver dependency or a specific incorrect Wine API. `adhesive-wine-debug.log` has only80 lines and no relevant loader/SEH exception trace.

## Dump inventory

`minidump-summary.json` parses the header, stream directory, module list and exception stream of all20 existing dumps in both runtime directories. Seventeen record `CoreRT+0x1B6DF`; one records `CoreRT+0x528D9`; two copies record `legitimacy+0x66B924`. None has Adhesive in its mapped-module list. These are historical dumps and do not capture the demonstrated Adhesive initializer failure. Absence after a failed load/unload cannot prove Adhesive never ran earlier.

The JSON contains only artifact names, hashes, sizes, exception addresses and module basenames; no captured memory, credentials or authentication values.

## MSVCP140 missing data exports: a real, unresolved dependency caveat

The standalone v3 trace lines12037-12044 report eight unresolved `MSVCP140.dll` imports from CoreRT, with loader stubs at `0x6C0000` through `0x6C00FC`. `llvm-undname` identifies these as **data**, not functions: static `std::locale::id` objects for:

- `std::moneypunct<char, false>` and `<char, true>`;
- `std::moneypunct<wchar_t, false>` and `<wchar_t, true>`;
- `std::money_get<char>` and `<wchar_t>` with their default stream-buffer iterators;
- `std::money_put<char>` and `<wchar_t>` with their default stream-buffer iterators.

Installed CachyOS x64 `files/lib/wine/x86_64-windows/msvcp140.dll` SHA256: `32b6f1ae0fad5f3648e8aea1476270eda0ed2e3a57e33e83fcb61245dc48331a`. Its PE export table has none of these eight names, whereas corresponding num_get/num_put/numpunct IDs exist. The trace loads this built-in MSVCP140. Direct Adhesive import-table inspection finds MSVCP140 but no imports of these eight money IDs.

This matches known missing functionality in upstream source: [Wine msvcp140.spec](https://github.com/wine-mirror/wine/blob/master/dlls/msvcp140/msvcp140.spec) lacks these names, and [Wine locale implementation](https://github.com/wine-mirror/wine/blob/master/dlls/msvcp90/locale.c) lists money facets among missing facets. This is source evidence of unsupported C++ runtime functionality, not evidence that those facets caused the Adhesive failure.

[Wine loader import resolution](https://github.com/wine-mirror/wine/blob/master/dlls/ntdll/loader.c) calls `allocate_stub` when an import export is missing. The warning addresses are therefore placeholders, not working locale-ID data objects. A program reading such an address as data need not trigger the unimplemented-function exception that calling the stub would trigger. Consequently **zero exceptions during CoreRT preload does not prove these imports harmless**. Conversely the captured Adhesive fault is neither a stub call nor a direct data-export access, and its relation to locale functionality is unproven. Do not label all dependencies clean or patch these data objects with fake placeholders.

An official native VC++ runtime control in a separate isolated prefix, with exact DLL provenance/hashes and normal dependency loading, could distinguish this hypothesis. It would not require a protection change. No such control was executed by this audit.

### Existing native runtime candidates, inspected without execution

The main prefix `/home/feras/Games/FiveM-Official-Test/GTA-Prefix-Work/drive_c/windows/system32` already contains these non-Wine x64 DLLs. Matching copies of the three VC++ DLLs also exist in `../2026-11-04/private/Prefix-GE10-30/drive_c/windows/system32`. Neither prefix was changed.

| File | Bytes | Version resource | SHA256 |
| --- | ---: | --- | --- |
| msvcp140.dll | 557728 | 14.44.35211.0 | `0f885b509a685d2bbfa652fed26b5fb31d88fbdab0a978c641d1c7b8aa460aa9` |
| vcruntime140.dll | 124544 | 14.44.35211.0 | `d5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066` |
| vcruntime140_1.dll | 49792 | 14.44.35211.0 | `1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f` |
| ucrtbase.dll | 986504 | 10.0.10586.15 | `51cbbde17a768930300236facd9738f54b7801e6715771ff8af90bfbe3fad44f` |

The VC++ files have Microsoft Corporation/Microsoft C Runtime Library version-resource strings. Their PE certificate-table PKCS7 objects contain certificates with subject Microsoft Windows Software Compatibility Publisher, chained by embedded issuer names through Microsoft Windows Third Party Component CA2013 to Microsoft Root Certificate Authority2011. The UCRT file contains Microsoft Corporation / Microsoft Code Signing PCA2011 certificates. This is **metadata inspection**, not full Authenticode image-digest or trust verification; no `osslsigncode` is installed. Version-resource strings and embedded certificate subjects alone are not proof of authenticity. The exact historical installer/download source has not been established by this audit.

Native MSVCP140 exports all eight missing money facet IDs, at data RVAs `0x81F68` through `0x820C0`. Its ordinary import table requires both `vcruntime140.dll` and `vcruntime140_1.dll`, plus API-set UCRT dependencies. A first control should keep UCRT unchanged to avoid changing two hypotheses at once; the native UCRT candidate above is recorded separately.

## Follow-up controls reviewed independently

Five new parent-run offline tests are captured in [results-table.md](results-table.md), [results.json](results.json) and [trace-excerpts.txt](trace-excerpts.txt). The excerpt retains exact original log/probe-result line numbers and selects only the dynamically identified probe main thread. Other process output is excluded.

The native VC++ control actually loaded all three native DLLs with environment native-only order; their PROCESS_ATTACH routines succeeded and the eight unresolved data-import warnings disappeared. Official Adhesive nevertheless failed at the same `+0xD9FEC5` read with error998. A fifth control including the native UCRT also reached the same fault; the UCRT stack frame became `_initterm+0x4F` (native export RVA0x5160, frame0x51AF), versus `_initterm+0x2A` on Wine UCRT. Thus the eight missing locale IDs, CoreRT version and replacing built-in CRTs with these native CRTs are not sufficient explanations or repairs for this standalone failure. The underlying invalid pointer source and linkage to historical real-client failure remain unresolved.

No additional runtime tests were executed by this audit. The parent owns runtime substitution/restoration and signature-verification records.

## Recheck commands

Run from the project root. These inspect files without execution:

```sh
llvm-readobj --coff-exports /home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/tools/proton/Proton-CachyOS-latest/files/lib/wine/x86_64-windows/msvcp140.dll
llvm-readobj --coff-imports Run-Adhesive-Test/CoreRT.dll
llvm-readobj --coff-imports Run-Adhesive-Test/adhesive.dll
rg -n 'No implementation for MSVCP140' Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/adhesive-initialized-v3.log
```

Raw private logs and dumps should remain local. This report does not authorize publishing them.
