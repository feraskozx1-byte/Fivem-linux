#!/usr/bin/env python3
"""Build a guarded, diagnostic-only Wine prototype; never edit installed files.

This is a machine-code equivalent of loader-static-tls.patch, not a rebuild of
Wine. Only a public Wine loader branch changes; no export, TLS flag, callback,
or private FiveM/Adhesive binary changes. Full upstream build remains separate.
"""
from pathlib import Path
import difflib, hashlib, json, struct, subprocess

r=Path(__file__).resolve().parent
source=r/'public-source/dlls/ntdll/loader.c'
old=source.read_text()
before='''    if (!wm || wm->ldr.TlsIndex == -1)
        ret = STATUS_DLL_NOT_FOUND;
    else
        wm->ldr.Flags |= LDR_NO_DLL_CALLS;'''
after='''    if (!wm)
        ret = STATUS_DLL_NOT_FOUND;
    else if (wm->ldr.TlsIndex != -1)
        wm->ldr.Flags |= LDR_NO_DLL_CALLS;'''
assert old.count(before)==1
new=old.replace(before,after)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
    fromfile='a/dlls/ntdll/loader.c',tofile='b/dlls/ntdll/loader.c'))
(r/'loader-static-tls.patch').write_text(patch)
subprocess.run(['git','apply','--check',str(r/'loader-static-tls.patch')],cwd=r/'public-source',check=True)

original=Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/tools/proton/Proton-CachyOS-latest/files/lib/wine/x86_64-windows/ntdll.dll'
b=original.read_bytes()
expected='af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5'
assert hashlib.sha256(b).hexdigest()==expected, 'Different Wine build: stop, do not guess offsets'
# Verified disassembly: cmp TlsIndex,-1; je error. Redirect only that je to
# existing xor ebx,ebx (success), skipping the flag write. Other paths unchanged.
at=0x14813
assert b[at-5:at+18].hex()=='6683786eff74268148680000040031db4889f1e81a2602'
out=r/'private/wine-prototype';out.mkdir(mode=0o700,exist_ok=True)
asm=out/'static-tls-branch.s'
asm.write_text('.text\n.globl branch\nbranch:\n je success\n .space 7, 0x90\nsuccess:\n')
subprocess.run(['clang','--target=x86_64-pc-windows-msvc','-c',str(asm),'-o',str(out/'static-tls-branch.obj')],check=True)
subprocess.run(['llvm-objcopy','--dump-section','.text='+str(out/'static-tls-branch.bin'),str(out/'static-tls-branch.obj')],check=True)
branch=(out/'static-tls-branch.bin').read_bytes()[:2]
assert branch==bytes.fromhex('7407')
patched=bytearray(b);patched[at:at+2]=branch
assert [(i,x,y) for i,(x,y) in enumerate(zip(b,patched)) if x!=y]==[(at+1,0x26,0x07)]
target=out/'ntdll.dll'
if target.exists():assert target.read_bytes()==patched, 'Preserve a different previous prototype'
else:target.write_bytes(patched)
manifest={'kind':'source-backed binary prototype, NOT a full Wine source build',
 'source_url':'https://raw.githubusercontent.com/wine-mirror/wine/wine-11.0/dlls/ntdll/loader.c',
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'original_path':str(original),'original_sha256':expected,
 'prototype_sha256':hashlib.sha256(patched).hexdigest(),
 'changed_file_offset':hex(at+1),'old_byte':'26','new_byte':'07',
 'branch_RVA':hex(at),'old_target_RVA':'0x1483b','new_target_RVA':'0x1481c',
 'TLS_thread_callbacks_disabled':False,'export_table_changes':False,
 'installed_Proton_modified':False,'use':'private read-only mount namespace; dedicated test prefix only'}
(out/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
