# Adhesive loading and connection authentication — 2026-11-05

Scope: source, existing logs and PE metadata review, followed by a parent-coordinated isolated standalone-loader experiment documented below. No server connection was attempted and no existing client binaries, account configuration or security code were modified. This document contains no credentials, ticket values or cookies.

## Confirmed observations

The experimental DLL and official reference match byte for byte by SHA-256:

- `Official-Reference/adhesive-24769.dll`
- `Run-Adhesive-Test/adhesive.dll`
- SHA-256: `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`

Existing logs repeatedly record error 998 and substitution of Sticky:

- [experimental log, line 3](../../Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T192501.log#L3), also line 41;
- [experimental log, line 3](../../Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T191448.log#L3), also line 83;
- `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T194742.log:3`;
- `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log:3`.

[Microsoft documents 998 as ERROR_NOACCESS](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--500-999-): invalid access to a memory location. The error alone does not identify a faulting instruction, establish a kernel-driver dependency, or establish intentional environmental rejection.

[DllGameComponent.Win32.cpp:125](../../Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp#L125) calls LoadLibrary. Lines 138–147 contain the existing Wine-specific fallback to Sticky. Lines 203–207 also substitute Sticky when the Adhesive manifest cannot be loaded. Consequently a logical `pre-gameload component adhesive` message is insufficient evidence that the official DLL initialized successfully.

## PE metadata checks

Read-only `file`, `objdump -p`, `objdump -h` and a small Python standard-library header reader found:

- PE32+, x86-64, seven sections; all section raw-data ranges fit inside the file.
- Image base `0x180000000`, image size `0x0340d000`, entry-point RVA `0x02b98e48`.
- One named export: `CreateComponent`, RVA `0x001023a0`.
- Exception, relocation, TLS, load-configuration, resource and delay-import directories exist.
- Three TLS callback RVAs: `0x02b99120`, `0x000010d0`, `0x02b99198`.
- Delay-loaded library: `ole32.dll`.

These are structural observations, not proof of correct initialization. The previous finding of zero missing imported functions across 25 checked DLLs was accepted rather than redundantly repeated. Export presence cannot establish correct Wine API semantics, dynamically resolved dependencies or successful TLS/DllMain execution. No protected logic was disassembled or altered.

## Logging limits

`adhesive-wine-debug.log` contains Heroic wrapper output, not a Wine loader/exception trace. The inspected actual Heroic entry logs under `~/.var/app/com.heroicgameslauncher.hgl/.local/state/Heroic/logs/games/wC6nr6dqw6GVLd8H6ysDhV_sideload/launch.log` and `.old` also contained zero `trace:seh` and zero `trace:module` entries. No exact Adhesive fault stack is therefore available from these files.

`corert-crash-debug.log:30` contains an older access violation at CoreRT; it is not evidence identifying the later Adhesive fault. File traces showing absent Adhesive in Run-Test likewise concern a different directory and must not be relabeled as experimental-DLL load traces.

A future isolated loader/SEH trace would need to capture the first relevant exception and module mapping around LoadLibrary while preserving the current prefixes and runtime directories. This review did not launch such a test or claim its outcome.

## Meaning of the server authentication error

[InitConnectMethod.cpp:641](../../Original-PR4050-Source/code/components/citizen-server-impl/src/InitConnectMethod.cpp#L641) looks for `cfxTicket2`. Lines 643–645 emit `No authentication ticket was specified.` when that field is absent. This is the immediate server-side cause represented by the exact message, distinct from invalid-signature or expired-ticket validation.

[NetLibrary.cpp:1681](../../Original-PR4050-Source/code/components/net/src/NetLibrary.cpp#L1681) conditionally adds the separate Steam `authTicket`. The generic `Obtaining Steam ticket...` progress text at line 1665 does not establish which store owns the game or prove any ticket was issued.

[NetLibrary.cpp:1866](../../Original-PR4050-Source/code/components/net/src/NetLibrary.cpp#L1866) invokes `OnInterceptConnectionForAuth`; lines 1870–1873 merge additional POST fields supplied through its callback. Searching the local open source found the server-side `cfxTicket2` check but no literal client-side `cfxTicket2` producer. Closed-source components or other dynamically supplied code could produce or modify the field; this search cannot establish exclusive ownership by Adhesive.

Existing missing-ticket examples include `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T182632.log:210,352`. Some logs were copied between test directories; directory placement alone must not establish the DLL loaded during a historical run.

Successful Cfx.re account linking is separate evidence from successful per-connection ticket issuance. The combination of unavailable original protection initialization and missing cfxTicket2 supports a security-component integration blocker. It does not prove that error 998 alone explains every missing-ticket event or exclude other normal authentication faults.

## Existing security-sensitive baseline

These changes predate this investigation and were not created, expanded or modified here:

- [WineCompat.Win32.cpp:34](../../Original-PR4050-Source/code/client/citicore/WineCompat.Win32.cpp#L34), lines 34–45, intercepts GetProcAddress and hides Wine identity exports; lines 67–79 install the hook.
- [ComponentLoader.cpp:175](../../Original-PR4050-Source/code/client/citicore/ComponentLoader.cpp#L175), lines 175–193, changes the Wine insecure-mode selection inherited from upstream.
- DllGameComponent fallback paths described above replace the official component with Sticky when it fails.

A working menu, disappearance of an insecure-mode warning, or Sticky initialization does not validate the original security stack. No source modifications in these security-sensitive paths were authorized or performed by this subtask.

## Upstream support evidence

On 2026-11-05, the original [Cfx review comment](https://github.com/citizenfx/fivem/pull/4050#discussion_r4289067271) was re-read using the GitHub connector endpoint `/repos/citizenfx/fivem/pulls/comments/4289067271`. Its creation and update timestamps remain 2026-10-15. The maintainer states that Linux secure-server connections are not currently intended to be permitted. The live PR page remains open.

This establishes an upstream support restriction. It is not an experimentally measured proof of the exact code path producing error 998 or every missing-ticket event, and does not establish a specific kernel-driver requirement.

## Fixes, blockers and rebuild

No Adhesive/authentication fix is justified by the available evidence, and none was applied. The isolated version-3 experiment below now supplies an initialization fault stack, while a trace in the actual fully initialized FiveM host remains unavailable. A supported protected-server outcome additionally requires original component support and acceptance by Cfx.

A source rebuild of CoreRT can deliver independent ordinary compatibility fixes, but cannot rebuild the proprietary official Adhesive DLL and does not by itself demonstrate that cfxTicket2 will be supplied. No full build, DLL replacement, identity impersonation, ticket forgery or authentication/security bypass was performed.


## Addendum: isolated standalone-loader experiment

The parent ran the newly compiled no-CRT `loader-probe.exe --adhesive` using Flatpak-bundled UMU and Proton-CachyOS in a fresh private prefix, with networking disabled and the client directory exposed read-only. The launcher returned exit 10 (the probe library-load-failure code). Version 1 stdout was not propagated, so the raw loader/SEH log, rather than stdout, is the evidence for the following observations. Version 2 subsequently adds prefix-local result files and completion markers; its results will be recorded separately by the parent.

Raw trace: `private/api-probe-cachyos/adhesive.log`. A bounded, sanitized excerpt retaining original line numbers is [standalone-adhesive-loader-excerpt.txt](standalone-adhesive-loader-excerpt.txt).

- Lines 11711 and 15267–15269 map Adhesive at `0x6ffff9270000` and begin dependency initialization.
- Line 15858 calls `net-tcp-server.dll` PROCESS_ATTACH, image base `0x6ffff7940000`.
- Lines 15872–15879 show `STATUS_ACCESS_VIOLATION` at `0x6ffff79412db`, which is **net-tcp-server.dll + 0x12db**, writing address **0x60**, with `rdx=0`.
- Lines 15880–15883 show the probe vectored logger observing the exception and returning zero (`EXCEPTION_CONTINUE_SEARCH`). It did not suppress or bypass the fault.
- The loader catches the exception and returns failure: line 15908 PROCESS_ATTACH returns zero; line 15911 explicitly reports net-tcp-server initialization failure.
- Lines 15912–15915 propagate initialization failure through `net-tcp-server.dll`, `http-client.dll`, `citizen-resources-client.dll`, then Adhesive. The trace does not reach an Adhesive DllMain fault.

**Interpretation and limit:** this experiment establishes a dependency initialization failure in the minimal standalone host. FiveM components can depend on host initialization that this tiny loader deliberately does not reproduce. The standalone trace therefore does **not** establish that net-tcp-server + 0x12db causes the original real-client Adhesive error 998, and it must not be called an internal Adhesive crash. No source or DLL change is justified from this synthetic-host fault alone. No anti-cheat check, environment identity or authentication mechanism was changed.


### Matching PDB and lifecycle analysis

[standalone-net-tcp-symbol-evidence.txt](standalone-net-tcp-symbol-evidence.txt) records reproducible `llvm-pdbutil` and bounded `objdump` evidence. The PE RSDS GUID `6613D39C-143C-45CD-B593-291B5DFD43D0`, age 1, matches `Run-Adhesive-Test/dbg/net-tcp-server.pdb`.

The fault belongs to `dynamic initializer for init`, RVA `0x1290`–`0x12e5`, in compiland `UvLoopManager.obj` (module 99). PDB line information maps this range to [UvLoopManager.cpp:57](../../Original-PR4050-Source/code/components/net-tcp-server/src/UvLoopManager.cpp#L57), whose constructor body at line 55 invokes `Instance<net::UvLoopManager>::Set(new net::UvLoopManager())`. Inlined Set ultimately writes the registry vector in [Registry.h:90](../../Original-PR4050-Source/code/client/shared/Registry.h#L90), through lines 189–196. The local files' SHA-256 values exactly match the PDB source checksums:

- UvLoopManager.cpp: `3edb94ff8655b4a0ff8300e936793ede2eb9e49f196b437fcc90927a2a7aebb8`.
- Registry.h: `5230eba6f18705af242195f1e1c1993b816517108e19950ef42b28ffb0df1260`.

The faulting instruction is `mov %rbx,(%rdx,%rcx,8)`. The trace has `rdx=0` and `rcx=12`, so the write target is `0 + 12*8 = 0x60`. The preceding helper at RVA `0x21470` is mapped by the PDB to the per-module `CoreGetGlobalInstanceRegistry` wrapper in Registry.h:109–127; the following read takes the vector pointer from the returned registry object.

[InstanceRegistry.cpp:12](../../Original-PR4050-Source/code/client/citicore/InstanceRegistry.cpp#L12) defines the global CoreRT registry; its constructor allocates its vector in Registry.h:76–79. The standalone trace maps CoreRT at lines 14679–14680 but does not run its PROCESS_ATTACH before the net-tcp-server initializer faults. This supports an uninitialized registry caused by the standalone dependency/host loading order. In contrast, the real launcher explicitly loads CoreRT first, e.g. [Main.cpp:992](../../Original-PR4050-Source/code/client/launcher/Main.cpp#L992), also lines 1023 and 1052, before invoking its component startup entry points.

The supported conclusion is a demonstrated standalone-host lifecycle limitation. This is not sufficient evidence of an ordinary bug in the correctly initialized FiveM host, and no net-tcp-server/registry patch was made. Resolving that limitation for a diagnostic host would require reproducing normal CoreRT load order, not bypassing authentication or protection.


### Version 3 follow-up experiment preparation

After mapping the synthetic initialization fault, the probe gained a separate `--adhesive-initialized` mode. It explicitly loads CoreRT before Adhesive, matching the ordinary launcher order, while avoiding EarlyMode_Init, WineCompat_InstallHooks and component factories. Source inspection found the identity-hiding installation called explicitly from EarlyMode_Init only, with no static initializer in WineCompat.Win32.cpp and no custom CoreRT DllMain in the project source set. The diagnostic uses a distinct CREATE_NEW prefix result file and logs CoreRT exceptions separately (phase 5). It was rebuilt cleanly with warnings as errors; parent-coordinated execution/results are separate. Existing client DLLs remain untouched.


## Latest result: CoreRT-first Adhesive initialization test actually executed

The parent executed version 3's `--adhesive-initialized` mode offline using the same fresh private UMU/CachyOS prefix. The existing client directory remained read-only. The test first loaded the unchanged CoreRT.dll with the normal loader. The prefix result file confirms that preload succeeded and generated zero observed exceptions. This removes the earlier measured standalone registry-initialization failure from this test.

Evidence:

- [standalone-adhesive-initialized-result.txt](standalone-adhesive-initialized-result.txt): exact sanitized probe output, including `PROBE_EXIT_CODE=10`.
- [standalone-adhesive-initialized-excerpt.txt](standalone-adhesive-initialized-excerpt.txt): bounded trace excerpt with original line numbers.
- [standalone-adhesive-fault-instruction.txt](standalone-adhesive-fault-instruction.txt): only the single faulting instruction from the matching official DLL.
- Full private trace: `private/api-probe-cachyos/adhesive-initialized-v3.log`.

### Confirmed immediate cause in this controlled test

Adhesive mapped at `0x6ffff8f50000`. Trace line 15965 enters its PROCESS_ATTACH routine. Lines 16014–16021 show `STATUS_ACCESS_VIOLATION` inside **adhesive.dll + 0xD9FEC5**, while **reading address 0xA5D36A**. The vectored logger observed the exception and returned EXCEPTION_CONTINUE_SEARCH (line 16025). The loader caught the exception, the initialization routine returned zero (line 16050), and initialization failed (line 16053).

The result file independently records: CoreRT handle nonzero, `preload_core_error=0`, `core_exception_count=0`; Adhesive handle zero, `LoadLibraryExW_error=998`, one loader exception, and completion with exit 10. This is an actual measured load failure, not an inference from the launcher exit status alone.

The matching-file instruction at the fault RVA is `movzbl (%r9,%rax,1),%esi`: a one-byte memory read. Runtime `r9=0x7ad340` and `rax=0x2b002a` produce the logged invalid target `0xa5d36a`. Only this fault instruction was inspected; surrounding protection/check logic was not interpreted or modified.

### Initialization stage

The unwind trace at lines 16026–16033 contains Adhesive offsets `0xD9FEC5`, `0xD9DE92`, `0xD9DDC9`, `0xD9DC96`, `0xCC2457`, then `ucrtbase.dll + 0x3560A`, then Adhesive CRT offsets `0x2B98BC2` and `0x2B98D88`. Read-only export metadata from the actual prefix's ucrtbase.dll places `_initterm` at RVA `0x355E0`, so the frame is `_initterm + 0x2A`. Combined with the PROCESS_ATTACH entry, this supports a C/C++ static-initialization failure reached from Adhesive's CRT/DllMain initialization. The captured stack does not identify a TLS callback as the fault origin.

### What this does and does not establish

The experiment now establishes a real memory-read exception inside the unmodified official Adhesive DLL during initialization under the selected CachyOS runtime. Error 998 in this isolated test follows that exception. It identifies neither a specific missing/incorrect Windows API nor an intentional unsupported-platform check, and does not demonstrate a kernel-driver requirement.

This remains a minimal standalone host: CoreRT globals are initialized, but the complete FiveM launcher/component context is not reproduced. Accordingly, the original client error 998 cannot yet be assigned conclusively to this same RVA, and the broader reason the internal pointer is invalid remains unconfirmed. A normal-client first-fault trace or vendor-assisted symbols/analysis would be needed to close that gap. No authentication attempt or protected-server acceptance occurred. No DLL, anti-cheat check, Wine identity export or ticket was patched, forged or bypassed. Rebuilding open-source CoreRT alone does not repair the demonstrated closed-source initializer.
