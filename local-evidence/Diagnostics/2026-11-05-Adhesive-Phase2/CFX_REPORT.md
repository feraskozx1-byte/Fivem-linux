# Adhesive initialization read AV reproduced in real FiveM host under Wine

Prepared locally on 2026-11-05; not submitted. Offline startup diagnostics only. No server connections, authentication experiments, ticket changes, Wine masking or protection patches.

## New result beyond the standalone probe

The actual locally built FiveM.exe now reproduces the same proximal failure previously seen in the CRT-free CoreRT-first loader. Real-host module mapping, entry into Adhesive PROCESS_ATTACH, first scoped exception, unwind, failed return, and the client's own GetLastError998 log are all captured.

```
PID:TID                   014c:0150
Adhesive base             0x6FFFF56E0000
Exception IP              0x6FFFF647FEC5
RVA                       0xD9FEC5
Exception                 0xC0000005, read
Read target               0x20E6732
r9                        0x1FB6720
rax                       0x130012
PROCESS_ATTACH return     0
Client error              998, followed by existing Sticky fallback
```

Uninstrumented-by-relay host trace lines19828,19877–19896,19909–19912 establish the chain. Client log line3 records error998. The ten observed unwind frames exactly match the earlier standalone test: Adhesive D9FEC5→D9DE92→D9DDC9→D9DC96→CC2457, UCRT _initterm+0x2A, Adhesive CRT startup and Wine loader frames. CoreRT, legitimacy and dependencies initialize before Adhesive. This is not an inference from a Sticky pre-gameload log or error998 alone.

The historical original full-client run still lacks its own first-fault stack; this report describes a new controlled real-host reproduction.

## Additional bounded observations

A separate +virtual host run reproduces RVA D9FEC5 with target0x2046E02. Wine's last recorded view shows it in reserved but uncommitted subrange0x2030000–0x269FFFF; the committed portion ends0x202FFFF. This is internal lifecycle logging, **not VirtualQuery**. Earlier standalone MEM_FREE findings must not be applied to this process. No valid /proc map snapshot of the actual host was obtained; wrapper maps were rejected. That memory run's pipe ends after the exception target, so use the earlier host run for the full stack.

A separate Wine relay run, filtered using RelayFromInclude=adhesive.dll, reproduces the same RVA. At lines34162–34163, public malloc(0xD8000) returns0x1EF3820. At fault lines34303–34304, r9 is numerically the same pointer and rax=0x130012, yielding target0x2023832. This is0x58012 bytes beyond the end of the observed allocation request. No public free/realloc of that pointer was observed between allocation and fault. The numerical correspondence supports an out-of-request-bounds read; the object's intended meaning, lifetime and index provenance remain unknown.

Nearby NT open/query/allocate/read/close/free calls return STATUS_SUCCESS. This is not proof of correct byte counts, data contents or all API semantics. Void-function relay return-register values are not classified as errors. No public Windows API defect has been established. Relay adds extra instrumentation frames; the exact ten-frame equality above refers to the non-relay host trace.

## Binaries and environment

- Adhesive: 54,552,672 bytes, SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`, local official-reference version1.0.0.24769. Binary unchanged.
- CoreRT: SHA256 `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64`, previous targeted CI artifact42019993897.
- FiveM.exe: SHA256 `0f70ea0ee9ccdcf83bdebacf588722770bc0a28c95ce19ee1dc5575344c9819f`.
- Local source baseline PR4050 head `ba07d9d3d5bd8459b69a81c69eb6065d4e11273c`, with the preexisting compatibility changes documented in source-diff-before.patch. The Wine-masking startup call is absent; it was not re-enabled.
- Correct CoreRT PDB GUID D93B51AE-64C4-4ABA-8422-9C9CA823303A, age1. The PDB originally next to the rebuilt runtime was stale; only the isolated diagnostic symbol overlay uses the matching artifact PDB.
- Wine11.0 (CachyOS), Proton cachyos-11.0-20261015-slr, Heroic Flatpak2.22.4/runtime26.08, Ubuntu on PS5 AMD Zen2 hardware as reported by owner. No graphics/gameplay compatibility claim.

PE local version1.0.0.1 is generated with CI_PIPELINE_ID default1; it is not sufficient to establish ABI mismatch against Adhesive24769. Please confirm the supported host/component set and any private ABI requirements for this precise hash.

## Reproduction method

The actual FiveM.exe is copied into an isolated runtime root, with the same components.json and existing development-build marker. The rebuilt CoreRT and official Adhesive are symlinked from read-only source mounts. Writable cache/log directories are local; large immutable game-cache files are read-only links. Preparation copies about5.1MB, not the multi-GB runtime. An existing account-free diagnostic Wine prefix is used and networking is disabled by Flatpak.

The first host attempt fails before Adhesive in unsupported WindowsXamlManager activation. Setting FiveM's existing CitizenFX_NoTenUI=1 selects the existing legacy updater UI and permits the real component initialization path. No UI or security source patch was introduced. The runner stops after collecting Adhesive's loader outcome, with a45s deadline and12MiB log cap. The normal startup can advance briefly before termination; no connection action is supplied.

Using the prepared layout: `python3 run-fullhost.py --tag unique-host-tag --legacy-ui`. Optional public API observation: `python3 run-api-trace.py unique-api-tag`. These scripts currently contain owner-specific local paths; adapt only to a reviewed developer diagnostic environment. The API wrapper backs up/restores diagnostic user.reg; it changes logging only, never return values or exceptions. Instructions and recovery are in REPORT_AR.md. Runtime source files and main prefix are not replaced.

## Evidence package and request

Review locally: fullhost-comparison.json, fullhost-trace-excerpt.txt, memory-observation.json, memory-trace-excerpt.txt, api-observation.json, api-trace-excerpt.txt, CoreRT-PDB-validation.txt, CoreRT-EarlyMode-disassembly.txt, and the runner/preparation sources. Raw logs, registry backups, /proc metadata, dumps and account directories are not proposed for automatic upload. No proprietary DLL needs redistribution with this report.

Please symbolicate the initializer at these RVAs, identify the buffer/index provenance and expected input, and confirm its host initialization/ABI requirements. An approved diagnostic build logging lengths and API outcomes without private data would let us distinguish unsupported implementation assumptions from a reproducible public-API Wine defect. No native Windows comparison environment is available in the current session, so none is claimed or simulated.

Status: real-host initialization failure reproduced; no demonstrated general API root cause or operational fix; original security functionality has not initialized or been validated. No check bypass, identity concealment, fake protection DLL or exception suppression is proposed.
