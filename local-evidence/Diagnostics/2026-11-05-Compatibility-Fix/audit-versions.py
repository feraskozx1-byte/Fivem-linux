#!/usr/bin/env python3
from pathlib import Path
import mmap,struct,json,hashlib,datetime,uuid,subprocess,re
out=Path(__file__).resolve().parent; project=out.parents[1]
major={'FiveM.exe','CoreRT.dll','CitizenGame.dll','legitimacy.dll','adhesive.dll','sticky.dll','v8-9.3.345.16.dll','node.dll','net-tcp-server.dll','net-base.dll','citizen-resources-core.dll','vfs-core.dll','http-client.dll'}

def inspect(p,hash_it):
 with p.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as b:
  u16=lambda x:struct.unpack_from('<H',b,x)[0];u32=lambda x:struct.unpack_from('<I',b,x)[0]
  pe=u32(60);op=pe+24;secs=[]
  assert b[pe:pe+4]==b'PE\0\0'
  for i in range(u16(pe+6)):
   s=op+u16(pe+20)+i*40;secs.append((u32(s+12),max(u32(s+8),u32(s+16)),u32(s+20)))
  def off(r):
   for a,n,s in secs:
    if a<=r<a+n:return s+r-a
   if r<u32(op+60):return r
   raise ValueError(hex(r))
  dd=op+(112 if u16(op)==0x20b else 96)
  record={'path':str(p.relative_to(project)),'bytes':len(b),'machine':hex(u16(pe+4)),'coff_timestamp_raw':u32(pe+8),'manifest':None,'pdb':None,'repro_debug':False}
  record['coff_timestamp_utc_if_timestamp']=datetime.datetime.fromtimestamp(record['coff_timestamp_raw'],datetime.timezone.utc).isoformat()
  rr=u32(dd+16)
  def rname(v):
   if v>>31:
    o=off(rr)+(v&0x7fffffff);return b[o+2:o+2+u16(o)*2].decode('utf-16le')
   return v
  def tree(o,keys,depth=0):
   if depth>3:return
   pos=off(rr)+o;n=u16(pos+12)+u16(pos+14)
   for i in range(n):
    a,v=struct.unpack_from('<II',b,pos+16+i*8);k=rname(a)
    if not keys and k not in [16,115]:continue
    if v>>31:yield from tree(v&0x7fffffff,keys+[k],depth+1)
    else:
     q=off(rr)+v;rva,size=struct.unpack_from('<II',b,q);yield keys+[k],bytes(b[off(rva):off(rva)+size])
  if rr:
   for keys,data in tree(0,[]):
    if keys[0]==115 and keys[1]=='FXCOMPONENT':
     try:record['manifest']=json.loads(data.rstrip(b'\0').decode('utf-8-sig'))
     except (ValueError,UnicodeError):record['manifest_parse_error']=True
    if keys[0]==16:
     i=6
     while i+1<len(data) and data[i:i+2]!=b'\0\0':i+=2
     v=(i+2+3)&~3
     if len(data)>=v+52 and struct.unpack_from('<I',data,v)[0]==0xfeef04bd:
      fixed=struct.unpack_from('<13I',data,v)
      for label,idx in [('file_version',2),('product_version',4)]:
       a,c=fixed[idx:idx+2];record[label]='.'.join(map(str,[a>>16,a&65535,c>>16,c&65535]))
  dr,sz=u32(dd+48),u32(dd+52)
  if dr:
   for i in range(sz//28):
    d=off(dr)+i*28;typ=u32(d+12)
    if typ==16:record['repro_debug']=True
    if typ==2:
     q=u32(d+24)
     if b[q:q+4]==b'RSDS':record['pdb']={'guid':str(uuid.UUID(bytes_le=bytes(b[q+4:q+20]))),'age':u32(q+20),'embedded_path':bytes(b[q+24:b.find(b'\0',q+24)]).decode(errors='replace')}
  if hash_it:
   h=hashlib.sha256()
   for i in range(0,len(b),1024*1024):h.update(b[i:i+1024*1024])
   record['sha256']=h.hexdigest()
  return record
records=[]
for folder in ['Run-Adhesive-Test','Run-CoreRT-Test','Compiled-Release']:
 for p in sorted((project/folder).iterdir()):
  if p.is_file() and p.suffix.lower() in ['.dll','.exe']:
   records.append(inspect(p,p.name in major))
records.append(inspect(project/'Official-Reference/adhesive-24769.dll',True))
# Semantic dependency coverage using public ComponentId category-prefix/version rules.
def ident(s):
 m=re.fullmatch(r'([^\[]+)(?:\[([^\]]+)\])?',s);assert m,s
 ver=tuple(map(int,(m[2] or '0').split('.')));return m[1].split(':'),(ver+(0,)*4)[:4]
def matches(req,provided):
 a,v=ident(req);b,w=ident(provided);return b[:len(a)]==a and v<=w
coverage={}
for folder in ['Run-Adhesive-Test','Run-CoreRT-Test','Compiled-Release']:
 selected=[r for r in records if r['path'].startswith(folder+'/') and r['manifest']]
 # fx is a built-in provider: recorded separately, not falsely marked missing DLL.
 providers=['fx[2]','platform:windows']
 for r in selected:
  m=r['manifest'];providers += [m['name']+'['+m['version']+']']+m.get('provides',[])
 missing=[]
 for r in selected:
  for req in r['manifest'].get('dependencies',[]):
   if not any(matches(req,p) for p in providers):missing.append({'file':r['path'],'dependency':req,'loader_optional_category':ident(req)[0][0] in ['vendor','legitimacy']})
 coverage[folder]={'manifests':len(selected),'unresolved_declared_dependencies':missing}
(out/'versions.json').write_text(json.dumps({'records':records,'manifest_coverage':coverage},indent=2)+'\n')
(out/'git-status-before.txt').write_bytes(subprocess.check_output(['git','-C',str(project/'Original-PR4050-Source'),'status','--short']))
print('PE records',len(records));print({k:{'manifests':v['manifests'],'nonoptional_unresolved':[m for m in v['unresolved_declared_dependencies'] if not m['loader_optional_category']]} for k,v in coverage.items()})

