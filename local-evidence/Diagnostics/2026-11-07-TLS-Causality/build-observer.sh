#!/usr/bin/env bash
set -euo pipefail
tls_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cp "$tls_dir/../2026-11-05-Adhesive-Index-Trace/trace-kernel32.def" "$tls_dir/observer-kernel32.def"
llvm-dlltool -m i386:x86-64 -d "$tls_dir/observer-kernel32.def" -l "$tls_dir/observer-kernel32.lib"
for tls_mode in host fixture; do
 tls_flags=()
 if [[ "$tls_mode" == fixture ]]; then tls_flags=(-DOWN_FIXTURE=1); fi
 clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror "${tls_flags[@]}" -c "$tls_dir/api-observer.c" -o "$tls_dir/api-observer-$tls_mode.obj"
 lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$tls_dir/api-observer-$tls_mode.exe" "$tls_dir/api-observer-$tls_mode.obj" "$tls_dir/observer-kernel32.lib"
done
