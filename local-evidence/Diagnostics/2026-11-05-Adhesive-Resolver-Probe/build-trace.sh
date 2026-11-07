#!/usr/bin/env bash
set -euo pipefail
trace_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cp "$trace_dir/../2026-11-05-Adhesive-RCA/observer-kernel32.def" "$trace_dir/trace-kernel32.def"
printf '%s\n' SetThreadContext >> "$trace_dir/trace-kernel32.def"
llvm-dlltool -m i386:x86-64 -d "$trace_dir/trace-kernel32.def" -l "$trace_dir/trace-kernel32.lib"
clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror -c "$trace_dir/index-fixture.c" -o "$trace_dir/index-fixture.obj"
lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$trace_dir/index-fixture.exe" "$trace_dir/index-fixture.obj" "$trace_dir/trace-kernel32.lib"
python3 - "$trace_dir" <<'PY'
from pathlib import Path
import re,subprocess,sys
p=Path(sys.argv[1]);s=subprocess.check_output(['llvm-readobj','--coff-exports',str(p/'index-fixture.exe')],text=True)
definitions=[]
for name,macro in [('IndexBoundary','FIXTURE_RVA'),('LimitBoundary','FIXTURE_LIMIT_RVA'),('ReturnBoundary','FIXTURE_RETURN_RVA')]:
 rva=re.search(r'Name: '+name+r'\s+RVA: (0x[0-9a-fA-F]+)',s)[1]
 definitions.append('#define '+macro+' '+rva+'\n')
(p/'fixture-rva.h').write_text(''.join(definitions))
PY
for trace_mode in host fixture; do
  trace_flags=()
  if [[ "$trace_mode" == fixture ]]; then trace_flags=(-DFIXTURE_MODE=1); fi
  clang --target=x86_64-pc-windows-msvc -std=c11 -O1 -funwind-tables -fno-stack-protector -fno-builtin -Wall -Wextra -Werror "${trace_flags[@]}" -c "$trace_dir/index-observer.c" -o "$trace_dir/index-observer-$trace_mode.obj"
  lld-link /nologo /machine:x64 /subsystem:console /entry:mainCRTStartup /nodefaultlib /dynamicbase /nxcompat /out:"$trace_dir/index-observer-$trace_mode.exe" "$trace_dir/index-observer-$trace_mode.obj" "$trace_dir/trace-kernel32.lib"
done
