#!/usr/bin/env bash
set -euo pipefail
rca_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
llvm-dlltool -m i386:x86-64 -d "$rca_dir/../2026-11-05-Compatibility-Fix/kernel32.def" -l "$rca_dir/probe-kernel32.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$rca_dir/export-probe.c" -o "$rca_dir/export-probe.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$rca_dir/export-probe.exe" "$rca_dir/export-probe.obj" "$rca_dir/probe-kernel32.lib"
