#!/usr/bin/env python3
"""Compare public name ranks, ordinal mappings and structural contracts only."""
from pathlib import Path
import json
r=Path(__file__).resolve().parent
a=json.loads((r/'ntdll-wine.json').read_text())
b=json.loads((r/'windows-reference/ntdll-windows-reference.json').read_text())
w={x['name']:x for x in a['exports']};n={x['name']:x for x in b['exports']}
common=sorted(w.keys()&n.keys())
assert a['names_sorted'] and b['names_sorted']
assert [x['name'] for x in a['exports'] if x['name'] in n]==[x['name'] for x in b['exports'] if x['name'] in w]
examples=[]
for name in ['NtReadFile','NtAllocateVirtualMemory','LdrGetProcedureAddress','RtlSetSecurityObjectEx']:
    examples.append(dict(name=name,wine=w.get(name),windows=n.get(name)))
out=dict(
    wine={key:a[key] for key in ['file_sha256','number_of_names','number_of_functions','ordinal_base','size_of_image','names_sorted']},
    windows={key:b[key] for key in ['file_sha256','file_version','os','runner_image_version','number_of_names','number_of_functions','ordinal_base','size_of_image','names_sorted']},
    reference_scope='Native Windows Server2022 x64 public PE/GetProcAddress reference; not a FiveM-supported client certification.',
    native_GetProcAddress_mismatches=b['native_GetProcAddress_mismatches'],
    common_names=len(common),windows_only_count=len(n.keys()-w.keys()),wine_only_count=len(w.keys()-n.keys()),
    common_relative_lexical_order_identical=True,
    common_names_at_identical_absolute_index=sum(w[name]['index']==n[name]['index'] for name in common),
    common_names_at_different_absolute_index=sum(w[name]['index']!=n[name]['index'] for name in common),
    examples=examples,
    captured_index1477={'wine':a['captured_index_1477'],'windows':b['captured_index_1477'],
        'intended_Adhesive_export':'UNKNOWN; Windows index identity is not evidence of resolver intent'},
    windows_only_names=sorted(n.keys()-w.keys()),wine_only_names=sorted(w.keys()-n.keys()),
    conclusion='Different valid export sets explain different absolute ranks, not why Adhesive selected1477. No general API contract violation established.'
)
(r/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({key:out[key] for key in out if key not in ['windows_only_names','wine_only_names','examples']},indent=2))
