from pathlib import Path
import json,struct,sys
p=Path(sys.argv[1]);b=p.read_bytes();pe=struct.unpack_from('<I',b,60)[0];o=pe+24
image=struct.unpack_from('<Q',b,o+24)[0];rva,size=struct.unpack_from('<II',b,o+112+72)
sections=o+struct.unpack_from('<H',b,pe+20)[0]
def raw(r):
    for i in range(struct.unpack_from('<H',b,pe+6)[0]):
        vs,va,rs,rp=struct.unpack_from('<IIII',b,sections+40*i+8)
        if va<=r<va+rs:return rp+r-va
    raise ValueError(hex(r))
v=struct.unpack_from('<QQQQII',b,raw(rva));n=0
if v[3]:
    at=raw(v[3]-image)
    while n<32 and struct.unpack_from('<Q',b,at+n*8)[0]:n+=1
result={'TLS_raw_bytes':v[1]-v[0],'zero_fill':v[4],'characteristics':hex(v[5]),'callback_count':n,'has_normal_OS_import':struct.unpack_from('<I',b,o+112+8)[0]!=0}
print(json.dumps(result,indent=2))
assert v[1]-v[0]==0x54a0 and v[4]==0 and v[5]==0x500000 and n==3
assert result['has_normal_OS_import']
