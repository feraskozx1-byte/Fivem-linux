#!/usr/bin/env python3
"""Read-only PE export audit for the exact existing Adhesive dependencies.
Export presence is NOT an implementation/semantics test. No DLL is executed.
"""
from pathlib import Path
import json,mmap,re,struct
root=Path(__file__).resolve().parent
project=root.parents[1]
prefix=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32'
runtime=project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost'
source=json.loads((root/'imports.json').read_text())
cache={}

def path_for(name):
    for directory in [runtime,prefix]:
        candidate=directory/name
        if candidate.is_file():return candidate
        candidate=directory/name.lower()
        if candidate.is_file():return candidate
    return None

def exports(path):
    key=str(path.resolve())
    if key in cache:return cache[key]
    with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as b:
        u16=lambda o:struct.unpack_from('<H',b,o)[0]
        u32=lambda o:struct.unpack_from('<I',b,o)[0]
        pe=u32(60); opt=pe+24
        assert b[pe:pe+4]==b'PE\0\0' and u16(opt)==0x20b
        sections=[]
        for i in range(u16(pe+6)):
            off=opt+u16(pe+20)+i*40
            sections.append((u32(off+12),max(u32(off+8),u32(off+16)),u32(off+20)))
        def off(rva):
            for va,size,raw in sections:
                if va<=rva<va+size:return raw+rva-va
            if rva<u32(opt+60):return rva
            raise ValueError(hex(rva))
        def string(rva):
            start=off(rva); end=b.find(b'\0',start)
            return b[start:end].decode('ascii')
        er,esz=u32(opt+112),u32(opt+116)
        if not er:result=({},{});cache[key]=result;return result
        e=off(er); base,nfun,nnames,func,names,ords=struct.unpack_from('<IIIIII',b,e+16)
        byord={}
        for i in range(nfun):
            rva=u32(off(func)+i*4)
            if rva:byord[base+i]=string(rva) if er<=rva<er+esz else rva
        byname={string(u32(off(names)+i*4)):byord.get(base+u16(off(ords)+i*2)) for i in range(nnames)}
        result=byname,byord
        cache[key]=result
        return result

def resolve(dll,symbol,depth=0):
    if depth>8:return {'status':'forward-cycle-or-depth'}
    if dll.lower().startswith('api-ms-win-crt-'):dll='ucrtbase.dll'
    path=path_for(dll)
    if path is None:return {'status':'host-file-not-found','host':dll}
    names,ordinals=exports(path)
    value=ordinals.get(int(symbol[1:])) if symbol.startswith('#') else names.get(symbol)
    if value is None:return {'status':'export-absent','host':dll,'symbol':symbol}
    if isinstance(value,str):
        target,sep,nextsym=value.rpartition('.')
        if not sep:return {'status':'unparsed-forward','forward':value}
        if not target.lower().endswith('.dll'):target+='.dll'
        return resolve(target,nextsym,depth+1)
    return {'status':'export-present','host':dll}

log=project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost-legacy-ui/wine.log'
lines=log.read_text(errors='replace').splitlines()
attach_names={};attached={}
for no,line in enumerate(lines,1):
    if not line.startswith('014c:'):continue
    m=re.search(r'MODULE_InitDLL \(([0-9A-F]+) L"([^"]+)",PROCESS_ATTACH,.* - CALL',line)
    if m:attach_names[m[1]]=m[2].lower()
    m=re.search(r'MODULE_InitDLL \(([0-9A-F]+),PROCESS_ATTACH,.* - RETURN 1',line)
    if m and m[1] in attach_names:attached[attach_names[m[1]]]=no
rows=[];issues=[]
for entry in source['imports']:
    dll=entry['dll'];host='ucrtbase.dll' if dll.lower().startswith('api-ms-win-crt-') else dll.lower()
    symbols=[]
    for raw in entry['symbols']:
        name=re.sub(r' \(\d+\)$','',raw)
        if not name:name="#"+re.search(r"\((\d+)\)$",raw)[1]
        result=resolve(dll,name)
        symbols.append({'symbol':name,**result})
        if result['status']!='export-present':issues.append({'dll':dll,**symbols[-1]})
    rows.append({'dll':dll,'kind':entry['kind'],'count':len(symbols),
                 'observed_host':host,'host_attach_success_line':attached.get(host),
                 'symbols':symbols})
result={'sha256':source['sha256'],'tool':'llvm-readobj imports + read-only mmap PE export/forward resolution',
        'scope':'Export presence in existing test runtime/prefix only. API-set CRT names resolved to observed UCRT host. No code execution or API semantics claim.',
        'descriptors':len(rows),'symbols':sum(r['count'] for r in rows),'issues':issues,'dependencies':rows}
(root/'dependency-audit.json').write_text(json.dumps(result,indent=2)+'\n')
md=['# Adhesive public imports — local dependency audit','',
    'SHA256: `'+source['sha256']+'`','',
    'Presence of an export is not proof it is implemented correctly. Line numbers refer to Phase2/private/fullhost-legacy-ui/wine.log. CRT API-set contracts are resolved to ucrtbase; this is not a missing-DLL finding. Delay imports are marked separately.','',
    '| DLL / contract | Kind | Imports | Host attach success line |','| --- | --- | ---: | ---: |']
for row in rows:md.append('| '+row['dll']+' | '+row['kind']+' | '+str(row['count'])+' | '+str(row['host_attach_success_line'] or 'not established')+' |')
md+=['','## Exact symbol inventory','']
for row in rows:
    md+=['### '+row['dll']+' ('+row['kind']+')','', '```text']+[r['symbol'] for r in row['symbols']]+['```','']
(root/'IMPORTS.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'descriptors':result['descriptors'],'symbols':result['symbols'],'export_presence_issues':issues,'inventory_bytes':(root/'IMPORTS.md').stat().st_size},indent=2))
