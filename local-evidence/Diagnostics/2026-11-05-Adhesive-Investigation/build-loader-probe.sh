#!/usr/bin/env bash
set -euo pipefail
probe_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
llvm-dlltool -m i386:x86-64 -d "$probe_dir/loader-probe-kernel32.def" -l "$probe_dir/loader-probe-kernel32.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -gcodeview -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$probe_dir/loader-probe.c" -o "$probe_dir/loader-probe.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /debug /out:"$probe_dir/loader-probe.exe" /pdb:"$probe_dir/loader-probe.pdb" "$probe_dir/loader-probe.obj" "$probe_dir/loader-probe-kernel32.lib"
