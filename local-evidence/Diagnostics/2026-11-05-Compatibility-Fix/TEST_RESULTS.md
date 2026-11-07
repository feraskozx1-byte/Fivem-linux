# Actual tests

- Build: clang Windows x64 + llvm-dlltool + lld-link; no new SDK/tool installation. Source and three tiny owned DLL fixtures are in this directory.
- `private/contracts-1`: UMU startup timeout before any completed test. Not an API failure.
- `private/contracts-direct-1`: initial executable exited after5 checks because the harness lacked asynchronous EH metadata for hardware faults. The old exe/object/PDB/build script are preserved in private/build-before-async/.
- Fixed harness build adds `-fasync-exceptions`; llvm-readobj confirms three ExceptionHandler records.
- `private/contracts-async-1`: direct CachyOS Wine under Heroic Flatpak,48 checks passed,0 failed, exit0.
- `private/contracts-proton-verified`: requested UMU/Proton-CachyOS transport,48 checks passed,0 failed, exit0. Exact exe SHA256 `be222f89d07a953191abcc95295b4dc83daec63ec2bad7c6ad6060813300a1fd`.

Observed I/O: fixture EOF0x60FF9; request0x61000 returns success/count0x60FF9; tail read returns3; read starting at EOF returns STATUS_END_OF_FILE/count0. Unread canary bytes unchanged. Memory mixed committed/reserved protection fails with error487 and preserves the first page. Own loader FALSE fixture yields1114; own initializer AV yields998. None establishes Adhesive root cause.

Microsoft contract references: [VirtualProtect](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect), [NtReadFile](https://learn.microsoft.com/en-us/windows/win32/devnotes/ntreadfile), [_msize](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/msize), [_initterm](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/initterm-initterm-e). No native Windows reference run of this suite is claimed.

Reproduce sequentially:
```bash
bash Diagnostics/2026-11-05-Compatibility-Fix/build-tests.sh
python3 Diagnostics/2026-11-05-Compatibility-Fix/run-tests.py --tag unique-contracts-tag
```
Use a fresh tag. Only owned fixture/result files in the diagnostic prefix are created; fixture is removed and results archived. No network or FiveM library loads.
