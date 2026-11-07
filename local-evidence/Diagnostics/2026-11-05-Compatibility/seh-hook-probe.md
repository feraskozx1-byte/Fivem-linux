# Isolated SEH directory-hook strategy probe

`seh-hook-probe.c` is a separate no-CRT Windows x64 diagnostic. It does not load any FiveM, GTA, adhesive, or security DLL. Its only PE import is KERNEL32.dll. It creates `C:\compat-probe-seh-hook.txt` with CREATE_NEW, preserving previous output. Use only the disposable diagnostic prefix and selected second-Epic CachyOS runner. No game/prefix configuration is modified by the program.

This is an API lookup strategy integration probe, **not** a MinHook test, rebuilt CoreRT test, real game test, or test of raising/unwinding an exception.

Build: `bash build-seh-hook-probe.sh`. This uses local clang/llvm-dlltool/lld-link and no Windows SDK or CRT. Compilation with `-Wall -Wextra -Werror` passed. PE exception metadata is valid x64 format; current build's exception directory is 72 bytes (six RUNTIME_FUNCTION entries). `bash -n` passed; PE imports were inspected with llvm-readobj.

Executable SHA-256 at preparation: `5bcaf8cafbdd48cfce386027c137dc810a1bd3046c8d68ee5fc975a75e3e7436`.

The program:

1. Resolves public ntdll directory/table/entry APIs and verifies its own valid PE exception directory and lookup baseline.
2. Requires the exact 15-byte actual CachyOS `RtlImageDirectoryEntryToData` prologue `55 41 54 57 56 53 48 83 ec 20 48 8d 6c 24 20`. If different, exits before patching. These bytes are complete instructions and contain no PC-relative operands.
3. Copies its own exception table to distinct read-only scratch memory. The copied entries retain valid image-relative unwind RVAs referring to its own executable.
4. Allocates an executable scratch trampoline containing those original 15 bytes plus a 14-byte register-preserving absolute RIP-indirect jump back. It changes the directory entrypoint **in this diagnostic process's memory only** to the same kind of jump to a stub. It flushes instruction cache and restores page protection.
5. Uses production-equivalent stub semantics: override only its own module's mapped-image exception directory; all other requests go through the trampoline.
6. Requires direct directory lookup, exported table lookup, and actual potentially-inlined function-entry lookup to return pointers into the distinct copy, with the original image base and byte length. Compares nonexception, other-module, and raw-file requests to exact pre-hook return/size baselines.
7. Restores original 15 bytes and protection, flushes instruction cache, verifies original table/entry lookup behavior, frees scratch allocations, and exits zero on success. Explicit failure paths also attempt restoration before exit.

The application creates no worker threads. This deliberately narrow diagnostic does not implement MinHook's decoder, relocation, nearby allocation, or thread coordination. Do not reuse this handcrafted trampoline in production. No on-disk DLL is patched.

Output marker `STRATEGY_RESULT=direct_table_and_inlined_entry_use_distinct_copy; forwarding_matches_baseline` indicates lookup checks succeeded. `POST_RESTORE_RESULT=original_table_and_entry_recovered`, restoration result, and zero exit must also be observed. The process exit code is authoritative; the log's `PROBE_EXIT_CODE` is hexadecimal and may precede a final disk-flush/close error. Exit 5 indicates output CREATE_NEW failed (including an existing output file); exit 11 indicates prologue mismatch with no patch; exit 6 indicates disk-output failure; other nonzero values identify failed assertions or cleanup.

Prepared and statically validated only at the time this file was written. The parent agent will execute it in the isolated offline diagnostic prefix and record results separately.


Session execution update: subsequent offline UMU/CachyOS experiments were run by the primary agent in a new isolated prefix. See [EXPERIMENTS_AR.md](EXPERIMENTS_AR.md) and [live-probe-results.txt](live-probe-results.txt). The SEH strategy probe and ABI probe passed; initialized Adhesive load failed with error 998 at adhesive+0xD9FEC5. These are standalone diagnostics, not a rebuilt CoreRT/MinHook/full-client test. Existing runtime binaries and accounts were preserved.
