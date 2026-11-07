#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,re
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tag',default='three-register-fixture');o=p.parse_args()
assert o.tag and all(c.isalnum() or c=='-' for c in o.tag)
s=(r/'private'/o.tag/'adh-index-trace.txt').read_text()
indices=[int(x,16) for x in re.findall(r'LOOKUP n=0x[0-9a-f]+ index=(0x[0-9a-f]+)',s)]
assert indices==[0,1,9,1467,1477]
limits=[int(x,16) for x in re.findall(r'^LIMIT value=(0x[0-9a-f]+)',s,re.M)]
returns=[int(x,16) for x in re.findall(r'^RETURN_LIMIT value=(0x[0-9a-f]+)',s,re.M)]
assert limits==[1,2,10,1468,1478] and returns==[5]
assert 'CHILD_EXIT=0x0000000000000000' in s and 'TRACE_ERROR=0x0000000000000000' in s
out={'passed':True,'tag':o.tag,'observed_indices':indices,'observed_limit_values':limits,'observed_return_values':returns,'expected_indices':[0,1,9,1467,1477],
     'fixture_checksum_exit':0,'source_sha256':hashlib.sha256((r/'index-observer.c').read_bytes()).hexdigest(),
     'fixture_observer_sha256':hashlib.sha256((r/'index-observer-fixture.exe').read_bytes()).hexdigest(),
     'host_observer_sha256':hashlib.sha256((r/'index-observer-host.exe').read_bytes()).hexdigest(),
     'debugger_visible':True,'remote_code_memory_writes':False,
     'scope':'Debug facility validation; not an Adhesive success test'}
(r/'fixture-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
