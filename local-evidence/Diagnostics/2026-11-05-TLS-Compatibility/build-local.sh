#!/usr/bin/env bash
set -euo pipefail
tls_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$tls_dir/local-bin"
cp "$tls_dir/../2026-11-05-Compatibility-Fix/kernel32.def" "$tls_dir/tls-kernel32.def"
printf '%s\n' CreateThread CreateEventW SetEvent WaitForSingleObject DisableThreadLibraryCalls >> "$tls_dir/tls-kernel32.def"
llvm-dlltool -m i386:x86-64 -d "$tls_dir/tls-kernel32.def" -l "$tls_dir/tls-kernel32.lib"
for tls_file in tls-test tls-fixture; do
 clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$tls_dir/$tls_file.c" -o "$tls_dir/$tls_file.obj"
done
lld-link /nologo /machine:x64 /dll /entry:DllMain /nodefaultlib /dynamicbase /nxcompat /out:"$tls_dir/local-bin/tls-fixture.dll" "$tls_dir/tls-fixture.obj" "$tls_dir/tls-kernel32.lib"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$tls_dir/local-bin/tls-test.exe" "$tls_dir/tls-test.obj" "$tls_dir/tls-kernel32.lib"
