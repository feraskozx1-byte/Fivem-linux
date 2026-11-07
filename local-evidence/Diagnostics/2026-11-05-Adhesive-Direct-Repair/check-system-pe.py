#!/usr/bin/env python3
"""Validate public PE structures of ONLY the two actual initializer input files.
No analysis of Adhesive instructions, no patches and no DLL execution.
"""
from pathlib import Path
import json,struct,hashlib
out=Path(__file__).resolve().parent;project=out.parents[1]
base=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32'
results=[]
for name in ['ntdll.dll','win32u.dll']:
 b=(base/name).read_bytes();u16=lambda o:struct.unpack_from('<H',b,o)[0];u32=lambda o:struct.unpack_from('<I',b,o)[0]
 pe=u32(60);op=pe+24;assert b[:2]==b'MZ' and b[pe:pe+4]==b'PE\0\0';assert u16(pe+4)==0x8664 and u16(op)==0x20b
 image=u32(op+56);headers=u32(op+60);sections=[]
 for i in range(u16(pe+6)):
  o=op+u16(pe+20)+40*i;vs,va,rs,raw=struct.unpack_from('<IIII',b,o+8);nm=b[o:o+8].rstrip(b'\0').decode()
  assert raw+rs<=len(b),(name,nm,'raw overflow');assert va+max(vs,rs)<=image,(name,nm,'image overflow')
  sections.append({'name':nm,'virtual_size':vs,'rva':va,'raw_size':rs,'raw_offset':raw,'characteristics':hex(u32(o+36))})
 def off(rva,size=1):
  for s in sections:
   d=rva-s['rva']
   if 0<=d and d+size<=s['raw_size']:return s['raw_offset']+d
  if 0<=rva and rva+size<=headers:return rva
  raise AssertionError((name,hex(rva),size,'unbacked RVA'))
 def string(rva):
  o=off(rva);end=b.find(b'\0',o);assert end>=o
  text=b[o:end].decode('ascii');off(rva,end-o+1);return text
 er,es=struct.unpack_from('<II',b,op+112);e=off(er,40);ordinal_base,nf,nn,func,names,ords=struct.unpack_from('<IIIIII',b,e+16)
 off(func,nf*4);off(names,nn*4);off(ords,nn*2)
 export_names=[]
 for i in range(nn):
  index=u16(off(ords)+2*i);assert index<nf,(name,'ordinal index outside AddressOfFunctions')
  export_names.append(string(u32(off(names)+4*i)))
 assert export_names==sorted(export_names),(name,'export names not sorted')
 forwarded=0
 for i in range(nf):
  rva=u32(off(func)+i*4)
  if not rva:continue
  if er<=rva<er+es:
   assert '.' in string(rva);forwarded+=1
  else:off(rva)
 result={'file':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'machine':'AMD64','size_of_image':image,'size_of_code':u32(op+4),'base_of_code':u32(op+20),'sections':sections,'export_function_count':nf,'named_export_count':nn,'forwarder_count':forwarded,'ordinal_base':ordinal_base,'all_checks_passed':True,'limit':'Structural checks only. Not an official private initializer compatibility guarantee or proof of every PE field.'}
 results.append(result)
(out/'system-pe-validation.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['file','bytes','size_of_code','named_export_count','all_checks_passed']} for r in results],indent=2))
