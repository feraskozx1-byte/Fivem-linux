#!/usr/bin/env bash
set -euo pipefail
probe_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$probe_dir/file-probe.c" -o "$probe_dir/file-probe.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$probe_dir/file-probe.exe" "$probe_dir/file-probe.obj" "$probe_dir/../2026-11-05-Compatibility-Fix/kernel32.lib"
