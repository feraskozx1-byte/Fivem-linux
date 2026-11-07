#!/usr/bin/env bash
set -euo pipefail
bounds_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
llvm-dlltool -m i386:x86-64 -d "$bounds_dir/observer-kernel32.def" -l "$bounds_dir/kernel32.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$bounds_dir/resolver-fixture.c" -o "$bounds_dir/resolver-fixture.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$bounds_dir/resolver-fixture.exe" "$bounds_dir/resolver-fixture.obj" "$bounds_dir/kernel32.lib"
for bounds_mode in host fixture; do
 bounds_flags=()
 if [[ "$bounds_mode" == fixture ]]; then bounds_flags=(-DOWN_FIXTURE=1); fi
 clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror "${bounds_flags[@]}" -c "$bounds_dir/resolver-observer.c" -o "$bounds_dir/resolver-observer-$bounds_mode.obj"
 lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$bounds_dir/resolver-observer-$bounds_mode.exe" "$bounds_dir/resolver-observer-$bounds_mode.obj" "$bounds_dir/kernel32.lib"
done
