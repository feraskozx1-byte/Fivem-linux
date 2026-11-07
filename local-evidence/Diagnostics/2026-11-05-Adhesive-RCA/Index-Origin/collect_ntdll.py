#!/usr/bin/env python3
"""Public PE export metadata; --native also checks GetProcAddress on own NTDLL.
Never emits DLL bytes or absolute function addresses. No FiveM dependency.
"""
import argparse, ctypes, hashlib, json, os, platform, struct, sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--file',type=Path)
p.add_argument('--native',action='store_true')
p.add_argument('--file-version')
p.add_argument('--output',required=True,type=Path)
o=p.parse_args()
assert bool(o.file) != o.native, 'Choose --file or --native'
k=None;base=None
if o.native:
    assert sys.platform=='win32' and struct.calcsize('P')==8
    from ctypes import wintypes as w
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetModuleHandleW.argtypes=[w.LPCWSTR];k.GetModuleHandleW.restype=w.HMODULE
    k.GetModuleFileNameW.argtypes=[w.HMODULE,w.LPWSTR,w.DWORD];k.GetModuleFileNameW.restype=w.DWORD
    k.GetProcAddress.argtypes=[w.HMODULE,ctypes.c_char_p];k.GetProcAddress.restype=ctypes.c_void_p
    base=k.GetModuleHandleW('ntdll.dll');assert base
    name=ctypes.create_unicode_buffer(32768)
    assert k.GetModuleFileNameW(base,name,len(name))
    path=Path(name.value)
else:path=o.file
b=path.read_bytes()
def u16(at):return struct.unpack_from('<H',b,at)[0]
def u32(at):return struct.unpack_from('<I',b,at)[0]
assert b[:2]==b'MZ'
pe=u32(60);assert b[pe:pe+4]==b'PE\0\0'
assert u16(pe+4)==0x8664 and u16(pe+24)==0x20b
image=u32(pe+80);headers=u32(pe+84)
table=pe+24+u16(pe+20)
sections=[struct.unpack_from('<IIII',b,table+40*i+8) for i in range(u16(pe+6))]
def raw(rva,n=1):
    if rva<headers and rva+n<=min(headers,len(b)):return rva
    for vs,va,rs,rp in sections:
        if va<=rva and rva+n<=va+rs and rp+rva-va+n<=len(b):return rp+rva-va
    raise ValueError('RVA not backed by file: '+hex(rva))
def string(rva):
    at=raw(rva);end=b.index(0,at,at+min(8192,len(b)-at))
    return b[at:end].decode('ascii')
er,esz=u32(pe+136),u32(pe+140)
ep=raw(er,40);ordinal_base,nf,nn,af,an,ao=struct.unpack_from('<IIIIII',b,ep+16)
assert 0<nn<=nf<100000
ft,nt,ot=raw(af,4*nf),raw(an,4*nn),raw(ao,2*nn)
rows=[];mismatches=[]
for i in range(nn):
    nr=u32(nt+4*i);name=string(nr);ordinal=u16(ot+2*i);assert ordinal<nf
    fn=u32(ft+4*ordinal);assert 0<fn<image
    forward=string(fn) if er<=fn<er+esz else None
    match=None
    if k and not forward:
        match=k.GetProcAddress(base,name.encode('ascii'))==base+fn
        if not match:mismatches.append(name)
    rows.append(dict(index=i,name=name,ordinal_index=ordinal,ordinal=ordinal_base+ordinal,
        name_rva=nr,function_rva=fn,forwarder=forward,native_GetProcAddress_match=match))
names=[r['name'] for r in rows]
assert names==sorted(names) and len(set(names))==nn
out=dict(mode='native public API reference' if k else 'file metadata only',
    source=str(path),file_sha256=hashlib.sha256(b).hexdigest(),file_version=o.file_version,
    os=platform.platform() if k else None,
    runner_image=os.environ.get('ImageOS') if k else None,
    runner_image_version=os.environ.get('ImageVersion') if k else None,
    machine='AMD64',optional_header='PE32+',size_of_image=image,
    ordinal_base=ordinal_base,number_of_functions=nf,number_of_names=nn,
    export_directory_rva=er,address_functions=af,address_names=an,address_ordinals=ao,
    names_sorted=True,direct_named_exports=sum(r['forwarder'] is None for r in rows),
    native_GetProcAddress_mismatches=mismatches if k else None,
    captured_index_1477=rows[1477] if 1477<nn else None,exports=rows)
with o.output.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({key:out[key] for key in out if key!='exports'},indent=2))
assert not mismatches
