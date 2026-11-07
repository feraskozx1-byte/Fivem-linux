# Standalone no-CRT Windows loader probe

Built on 2026-11-05 with clang 21.1.8 (`--target=x86_64-pc-windows-msvc`), llvm-dlltool and lld-link. No Windows SDK, MinGW headers or MSVC runtime needed. Rebuild with `./build-loader-probe.sh` in this directory. The build writes only new diagnostic artifacts here; it does not update either client directory.

The executable was compiled and statically inspected. Its author did not execute it; parent-coordinated isolated runtime attempts are recorded separately. Version 2 added prefix-local disk output because UMU did not propagate stdout from the first attempt. Version 3 adds the explicit --adhesive-initialized mode described below. `file` confirms x64 PE32+ console format. `objdump` confirms only KERNEL32 imports, no CRT imports and an exception directory containing RUNTIME_FUNCTION entries. Compilation used `-Wall -Wextra -Werror` and passed. `bash -n build-loader-probe.sh` passed.

## Modes

- No argument: examine this probe executable's own PE exception directory. Dynamically resolve `RtlImageDirectoryEntryToData`, `RtlLookupFunctionTable`, and `RtlLookupFunctionEntry` from the actual ntdll. Compare the directory pointer, image bases and returned length. Output explicitly reports whether lookup length is an entry count or byte size. No game DLLs are loaded in this mode.
- `--adhesive`: call `LoadLibraryExW` on the fixed absolute path `Z:\home\feras\Projects\FiveM-PR4050-Test\Run-Adhesive-Test\adhesive.dll`, using `LOAD_WITH_ALTERED_SEARCH_PATH`. Log the resulting module handle and exact GetLastError on failure. This is an initialization-only test: CreateComponent is not invoked, and no authentication or server connection is requested. A fresh prefix needs its standard Z mapping and access to the host path.

- `--adhesive-initialized` (version 3): first explicitly load the fixed `Run-Adhesive-Test/CoreRT.dll` with LOAD_WITH_ALTERED_SEARCH_PATH, allowing its ordinary CRT globals to initialize before the Adhesive dependency graph. Then perform the same Adhesive load. A distinct CREATE_NEW result file is `C:\compat-probe-adhesive-initialized.txt`. No EarlyMode_Init, CreateComponent, WineCompat_InstallHooks or other component/security startup entry point is called. This corrects a measured standalone-host load-order limitation, not the original client.

All modes install a vectored exception logger. It records exception code, instruction address, module path/base/offset where resolvable and, for memory-access exceptions, access kind and target address. It **always returns EXCEPTION_CONTINUE_SEARCH**. It does not patch exception behavior, security logic, Wine identity or authentication. A loader can handle its own first-chance exceptions; their appearance is diagnostic evidence and does not automatically mean fatal failure.

Exception phase numbers: 1 = PE exception-directory query; 2 = function-table query; 3 = function-entry query; 4 = Adhesive LoadLibraryExW; 5 = explicit CoreRT LoadLibraryExW. The logger's module offset can identify faults in mapped DLL initialization, including TLS/DllMain, but this probe does not assign fault origin without the trace. It logs no incoming command line, environment, credentials or ticket values.

## Exit codes

- 0: ABI results classified successfully, or the explicit library load succeeded.
- 2: required ntdll export missing in ABI mode.
- 3: inconsistent function table, image base, entry location or unrecognized length semantics.
- 4: vectored exception logger installation failed.
- 5: prefix-local result file could not be created (including an existing result file).
- 6: writing, flushing or closing the result file failed.
- 10: explicit Adhesive load returned failure; inspect LoadLibraryExW_error.
- 11: explicit CoreRT preload failed; inspect preload_core_error.
- 64: unsupported argument.
- Any unhandled exception: Windows/Wine termination behavior is retained.

Version 2 opens `C:\compat-probe-abi.txt` or `C:\compat-probe-adhesive.txt` inside the selected prefix with CREATE_NEW, preserving any previous measurement. Every output fragment also goes to stdout. Normal completion writes `PROBE_EXIT_CODE`, flushes and closes the file before ExitProcess. A fatal exception may leave only a partial file without the completion marker. Use an isolated prefix under private Diagnostics and redirect stdout/stderr there as well. No client-directory output file is opened. A proprietary DLL's initialization can have side effects of its own, so the parent will choose the isolated environment and control execution. Successful initialization is not evidence of protected-server authentication or official compatibility support.


## CoreRT preload inspection

The local project defines CitiCore as a shared library and includes its ordinary C++ globals. No custom CoreRT DllMain was found in its source set. Searching the client/shared source finds the WineCompat_InstallHooks implementation and an explicit call only from EarlyMode_Init (EarlyMode.Win32.cpp:19). WineCompat.Win32.cpp contains no static initializer. The probe never calls that exported early startup path. Therefore source evidence does not indicate that LoadLibraryExW(CoreRT) alone installs the identity-hiding hook. This is a source inspection statement, not proof about arbitrary unexamined binaries.


Session execution update: subsequent offline UMU/CachyOS experiments were run by the primary agent in a new isolated prefix. See [EXPERIMENTS_AR.md](EXPERIMENTS_AR.md) and [live-probe-results.txt](live-probe-results.txt). The SEH strategy probe and ABI probe passed; initialized Adhesive load failed with error 998 at adhesive+0xD9FEC5. These are standalone diagnostics, not a rebuilt CoreRT/MinHook/full-client test. Existing runtime binaries and accounts were preserved.
