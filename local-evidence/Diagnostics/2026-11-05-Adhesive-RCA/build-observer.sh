#!/usr/bin/env bash
set -euo pipefail
rca_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cat "$rca_dir/../2026-11-05-Compatibility-Fix/kernel32.def" > "$rca_dir/observer-kernel32.def"
cat >> "$rca_dir/observer-kernel32.def" <<'DEFS'
CreateProcessW
WaitForDebugEvent
ContinueDebugEvent
DebugSetProcessKillOnExit
ReadProcessMemory
VirtualQueryEx
OpenThread
GetThreadContext
GetFinalPathNameByHandleW
GetTickCount64
TerminateProcess
DEFS
llvm-dlltool -m i386:x86-64 -d "$rca_dir/observer-kernel32.def" -l "$rca_dir/observer-kernel32.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$rca_dir/debug-observer.c" -o "$rca_dir/debug-observer.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$rca_dir/debug-observer.exe" "$rca_dir/debug-observer.obj" "$rca_dir/observer-kernel32.lib"
