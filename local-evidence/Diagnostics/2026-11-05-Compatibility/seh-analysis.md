## SEH source review (2026-11-05)

Inspected:
- `Original-PR4050-Source/code/client/citicore/SEHTableHandler.Win32.cpp`
- Existing local `seh-wine-fix.patch` and `.before-seh-fix.bak` (the latter equals git HEAD).
- `code/client/launcher/ExecutableLoader.cpp:240-295` and `code/client/citicore/LaunchMode.h`.
- `code/client/citicore/premake5.lua` (`CitiCore` project, `CoreRT.dll` output).
- `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T194742.log:27,35-36`, showing the fatal missing private helper in ROSLauncher.
- Primary Wine source: https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/ntdll/unwind.c (public lookup lines 240-254, x64 function-entry lookup lines 2168-2189).

Confirmed source defect: Windows private `RtlpxLookupFunctionTable` discovery is applied to Wine, which implements the public three-argument `RtlLookupFunctionTable` and calls unrelated helpers. Merely suppressing the Windows 8+ fatal message does not establish the ABI of a discovered Wine helper and still runs the unsupported memory-information query/disassembly. Absence of a Windows-private helper is not a missing Wine export.

Actual runner disassembly adds a decisive constraint: x64 `RtlLookupFunctionEntry` in the second-Epic CachyOS runner has `RtlLookupFunctionTable` inlined and calls `RtlImageDirectoryEntryToData` directly. Hooking the table export alone would miss that path. See `runtime-ntdll-analysis.md` for exact hash, RVAs and instructions.

Implemented explicit early Wine branch hooking the shared non-inlined `RtlImageDirectoryEntryToData` with the existing directory stub. Check export, hook creation and enabling failures; enable only that target. The stub returns the game unwind table only for the exact game module, exception directory, and mapped-as-image requests. Other requests forward. The entry lookup itself sets the correct game image base before invoking this helper. This avoids Wine entering the native Windows query/disassembler path and covers both table and entry lookup implementations. Keep native Windows discovery/guards. Correct both module lookup predicates to exclude `moduleEnd`, which caller supplies as base + SizeOfImage.

ABI: Wine public table lookup takes PC, image-base pointer, byte-length pointer. The shared directory helper takes module, mapped-as-image flag, directory index, byte-length pointer. `RtlLookupFunctionEntry` uses `size / sizeof(*func)`. The source stub correctly returns table size in BYTES; it must not substitute entry count. Both upstream source and actual runner disassembly confirm this. Existing launcher `RtlAddFunctionTable` is insufficient alone because Wine first consults a module's static table before its dynamic table list.

Scanner stability fix: `FindCallFromAddress` now stops when `ud_disassemble` returns zero. Previously decoder EOF could leave the loop running forever. Existing return/instruction-selection behavior and the `INT32_MAX` input buffer are unchanged; this guard does not establish readable-memory bounds.

MinHook is initialized by the existing global `InitMHWrapper mh` in the same source file. No duplicate initialization was added. A failed/uninitialized library status is detected by checked hook creation in the new Wine branch. Existing exception reporting/security-related hooks were not changed.

Preservation: source remains exclusively CRLF (527 CRLF, 0 bare LF after change). The report directory contains `SEHTableHandler.Win32.cpp.pre-session.bak`, reconstructing original git HEAD plus the verified existing local patch, so the user's pre-session local change is retained. Existing backups and `seh-wine-fix.patch` remain unchanged. No binary, Wine prefix or runtime directory was changed.

Validation: `python3 Diagnostics/2026-11-05-Compatibility/validate-seh.py` PASS using host g++ C++17, ASan and UBSan. The script extracts production override/setup functions and supplies mock Win32/MinHook APIs. It checks Wine early directory-hook path avoids version queries/disassembly; 18 combinations of module/directory/mapping with exact forwarding; byte size; six downlevel boundary addresses; missing export/create/enable failures; and the native setup branch. Existing MSVC implicit function-pointer-to-void* assignments are explicitly cast only within the host harness. `validate-seh-scanner.py` also PASS with ASan/UBSan, extracting the production scanner and using a mocked udis86 decoder. It checks EOF at entry/after ordinary instruction/after one call, multiple calls, first-call mode, negative displacement, int3/nop, requested jump, and indirect call. The script recompiles the pre-fix scanner and confirms the EOF test detects the old infinite loop via a mock decoder call budget. This is not actual decoder testing. `git -c core.whitespace=cr-at-eol diff --check` PASS.

Limitations: this is not an actual Windows DLL compilation, MinHook patch/trampoline test or Wine exception-unwinding integration test. An incremental Windows x64 `CitiCore` target build is required to place the fix in `CoreRT.dll`; it has not been built or deployed. Runtime success remains unproven until rebuilt binaries are tested in an isolated test copy. No full rebuild was run.


Session execution update: subsequent offline UMU/CachyOS experiments were run by the primary agent in a new isolated prefix. See [EXPERIMENTS_AR.md](EXPERIMENTS_AR.md) and [live-probe-results.txt](live-probe-results.txt). The SEH strategy probe and ABI probe passed; initialized Adhesive load failed with error 998 at adhesive+0xD9FEC5. These are standalone diagnostics, not a rebuilt CoreRT/MinHook/full-client test. Existing runtime binaries and accounts were preserved.
