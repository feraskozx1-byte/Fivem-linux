#!/usr/bin/env bash
set -euo pipefail
suite_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cat > "$suite_dir/kernel32.def" <<'DEFS'
LIBRARY KERNEL32.dll
EXPORTS
GetStdHandle
WriteFile
CreateFileW
CloseHandle
DeleteFileW
FlushFileBuffers
ExitProcess
GetLastError
GetModuleHandleW
GetProcAddress
LoadLibraryW
FreeLibrary
GetModuleFileNameW
VirtualAlloc
VirtualFree
VirtualProtect
VirtualQuery
RaiseException
DEFS
cat > "$suite_dir/ntdll.def" <<'DEFS'
LIBRARY ntdll.dll
EXPORTS
__C_specific_handler
DEFS
llvm-dlltool -m i386:x86-64 -d "$suite_dir/kernel32.def" -l "$suite_dir/kernel32.lib"
llvm-dlltool -m i386:x86-64 -d "$suite_dir/ntdll.def" -l "$suite_dir/ntdll.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -gcodeview -funwind-tables -fasync-exceptions -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$suite_dir/contract-tests.c" -o "$suite_dir/contract-tests.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /debug /out:"$suite_dir/contract-tests.exe" /pdb:"$suite_dir/contract-tests.pdb" "$suite_dir/contract-tests.obj" "$suite_dir/kernel32.lib" "$suite_dir/ntdll.lib"
for kind in 0 1 2; do
  case "$kind" in 0) fixture_name=ok;; 1) fixture_name=false;; 2) fixture_name=av;; esac
  clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fasync-exceptions -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -DFIXTURE_KIND="$kind" -c "$suite_dir/fixture.c" -o "$suite_dir/fixture-$fixture_name.obj"
  lld-link /nologo /machine:x64 /dll /entry:DllMain /nodefaultlib /dynamicbase /nxcompat /out:"$suite_dir/compat-fixture-$fixture_name.dll" "$suite_dir/fixture-$fixture_name.obj"
done
