#!/usr/bin/env python3
"""Bounded checks of public hash families on observed public export names.
Does not emulate or modify proprietary code and does not identify intent alone.
"""
from pathlib import Path
import ctypes,json,re
r=Path(__file__).resolve().parent
text=(r/'private/resolver-comparisons/adh-index-trace.txt').read_text()
rows=[(int(i,16),int(v,16),int(t,16)) for v,t,i in re.findall(r'^RETURN_LIMIT value=(0x[0-9a-f]+) comparison_constant=(0x[0-9a-f]+) stack_index=(0x[0-9a-f]+)',text,re.M)]
w=json.loads((r.parent/'2026-11-05-Adhesive-RCA/Index-Origin/ntdll-wine.json').read_text())['exports']
mask=(1<<64)-1
xx=ctypes.CDLL('libxxhash.so.0')
xx.XXH64.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_uint64];xx.XXH64.restype=ctypes.c_uint64
xx.XXH3_64bits.argtypes=[ctypes.c_char_p,ctypes.c_size_t];xx.XXH3_64bits.restype=ctypes.c_uint64
city=ctypes.CDLL('libabsl_city.so.20260107')
ch=getattr(city,'_ZN4absl7debian913hash_internal10CityHash64EPKcm')
ch.argtypes=[ctypes.c_char_p,ctypes.c_size_t];ch.restype=ctypes.c_uint64
families={'XXH64_seed0':lambda b:xx.XXH64(b,len(b),0),'XXH3_64':lambda b:xx.XXH3_64bits(b,len(b)), 'CityHash64':lambda b:ch(b,len(b))}
def unxor(y,s):
    x=y
    for _ in range(64//s+1):x=y^(x>>s)
    return x&mask
def jenkins_seed(value,data,final):
    h=value
    if final:
        h=h*pow(32769,-1,1<<64)&mask;h=unxor(h,11);h=h*pow(9,-1,1<<64)&mask
    for c in reversed(data):
        h=unxor(h,6);h=h*pow(1025,-1,1<<64)&mask;h=(h-c)&mask
    return h
matches=[]
for form in ['exact','lower','upper']:
    for null in [False,True]:
        def data(i):
            s=w[i]['name'];s=s if form=='exact' else getattr(s,form)()
            return s.encode('ascii')+(b'\0' if null else b'')
        sample=rows[:12]
        for name,fn in families.items():
            values=[fn(data(i)) for i,v,t in sample]
            if all(h==v for h,(i,v,t) in zip(values,sample)):matches.append(dict(family=name,case=form,null=null,transform='direct'))
            if len({h^v for h,(i,v,t) in zip(values,sample)})==1:matches.append(dict(family=name,case=form,null=null,transform='constant XOR'))
        for final in [False,True]:
            seeds=[jenkins_seed(v,data(i),final) for i,v,t in sample]
            if len(set(seeds))==1:matches.append(dict(family='Jenkins64',case=form,null=null,final_mix=final,transform='consistent initial seed'))
out={'scope':'Public hash families only;12 observed public-name/value pairs','families':['XXH64(seed0)','XXH3_64','CityHash64','Jenkins64(with/without final mix)'],'matches':matches,'meaning':'No match does not identify the proprietary computation or prove a Wine defect.'}
(r/'public-hash-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
