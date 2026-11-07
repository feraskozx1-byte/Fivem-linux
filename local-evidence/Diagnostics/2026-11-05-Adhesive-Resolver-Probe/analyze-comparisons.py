#!/usr/bin/env python3
from pathlib import Path
import json,re
r=Path(__file__).resolve().parent
run=r/'private/resolver-comparisons'
s=(run/'adh-index-trace.txt').read_text()
rows=[tuple(int(x,16) for x in (i,v,t)) for v,t,i in re.findall(r'^RETURN_LIMIT value=(0x[0-9a-f]+) comparison_constant=(0x[0-9a-f]+) stack_index=(0x[0-9a-f]+)',s,re.M)]
assert len(rows)==1477 and [i for i,v,t in rows]==list(range(1477))
assert len({t for i,v,t in rows})==1 and all(v!=t for i,v,t in rows)
assert 'TRACE_ERROR=0x0000000000000000' in s and 'fault_rva=0x0000000000d9fec5' in s
markers=[]
for p in run.glob('CitizenFX_log*'):
    markers += [x for x in p.read_text(errors='replace').splitlines() if 'Adhesive failed to load under Wine (error ' in x]
assert any('error 998' in x for x in markers)
result={'comparison_site_RVA':'0xda4fc2','comparison_events':len(rows),'index_range':[0,1476],
    'declared_valid_names_compared':1468,'equal_comparison_results':0,
    'other_comparison_site_RVA':'0xda006c','other_comparison_events':len(re.findall(r'^LIMIT value=',s,re.M)),
    'actual_AV':'0xd9fec5','client_failure_markers':markers,
    'meaning':'A repeatable per-entry comparison did not match for any declared valid NTDLL name in this execution. Intended target and return contract remain unidentified.',
    'does_not_prove':'A specific missing public Windows API, or that the observed values are solely a standard hash of export names.',
    'loop_bound_hypothesis_result':'../2026-11-05-Adhesive-Loop-Limit/loop-bound-result.json;0x2800 loop-bound hypothesis rejected',
    'modified_runtime_DLLs':False,'security_initialization_success':False}
(r/'comparison-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
