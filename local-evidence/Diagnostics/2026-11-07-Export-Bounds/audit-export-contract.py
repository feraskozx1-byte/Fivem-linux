#!/usr/bin/env python3
"""New boundary/adjacency checks using existing native metadata; no DLL loading."""
from pathlib import Path
import collections,hashlib,json
r=Path(__file__).resolve().parent;old=r.parent/'2026-11-05-Adhesive-RCA/Index-Origin'
a=json.loads((old/'ntdll-wine.json').read_text());b=json.loads((old/'windows-reference/ntdll-windows-reference.json').read_text())
assert hashlib.sha256((r.parents[1]/a['source']).read_bytes()).hexdigest()==a['file_sha256']
results=[]
for label,d in [('Wine11.0',a),('WindowsServer2022',b)]:
 ex=d['exports'];nn=d['number_of_names'];nf=d['number_of_functions'];image=d['size_of_image']
 assert len(ex)==nn and [e['index'] for e in ex]==list(range(nn))
 names=[e['name'] for e in ex]
 assert len(set(names))==nn and names==sorted(names,key=lambda s:s.encode('ascii'))
 for table,length in [('address_functions',nf*4),('address_names',nn*4),('address_ordinals',nn*2)]:
  assert 0<=d[table]<=image and 0<=length<=image-d[table]
 assert all(0<=e['ordinal_index']<nf and 0<e['name_rva']<image and 0<e['function_rva']<image for e in ex)
 end=d['address_names']+4*nn
 assert end==d['address_ordinals']
 # Metadata records ordinal indices for each name, allowing this DWORD to be
 # reconstructed without downloading a Windows DLL or reading outside a table.
 word_after_names=ex[0]['ordinal_index']|(ex[1]['ordinal_index']<<16)
 results.append(dict(label=label,sha256=d['file_sha256'],names=nn,functions=nf,ordinal_base=d['ordinal_base'],
  name_table_start=hex(d['address_names']),name_table_end=hex(end),ordinal_table_start=hex(d['address_ordinals']),
  name_table_immediately_followed_by_ordinals=True,
  first_DWORD_after_names_reconstructed_from_ordinal_metadata=hex(word_after_names),
  first_DWORD_after_names_is_NULL_sentinel=word_after_names==0,
  named_ordinals_in_range=True,ordinal_only_function_slots=nf-len({e['ordinal_index'] for e in ex}),
  duplicate_names=0,ASCII_lexical_order=True,all_table_extents_fit_image=True))
w={e['name']:e for e in a['exports']};n={e['name']:e for e in b['exports']};common=w.keys()&n.keys()
assert [e['name'] for e in a['exports'] if e['name'] in common]==[e['name'] for e in b['exports'] if e['name'] in common]
windows_rvas=collections.defaultdict(list)
for e in b['exports']:windows_rvas[e['function_rva']].append(e['name'])
shared=[]
for name in sorted(n.keys()-w.keys()):
 present=[s for s in windows_rvas[n[name]['function_rva']] if s in w]
 if present:shared.append(dict(missing_Windows_name=name,other_Windows_names_at_same_RVA_present_in_Wine=present))
out=dict(inputs={'wine':str((old/'ntdll-wine.json').relative_to(r.parents[1])),
 'native':str((old/'windows-reference/ntdll-windows-reference.json').relative_to(r.parents[1])),
 'native_CI_run':42088585400,'new_native_run':False},tables=results,
 common_names=len(common),Windows_only_names=sorted(n.keys()-w.keys()),Wine_only_names=sorted(w.keys()-n.keys()),
 common_relative_order_identical=True,
 missing_names_sharing_reference_RVA_with_present_names=shared,
 same_RVA_does_not_establish_implementation_equivalence=True,
 conclusions={'Wine_specific_missing_NULL_name_sentinel':False,
  'Wine_name_table_malformed_in_checked_fields':False,
  'different_export_set_or_order_alone_identifies_Adhesive_target':False,
  'required_iterator_bound':'name_index < NumberOfNames, independent of OrdinalBase or NumberOfFunctions',
  'specific_missing_API_required_by_Adhesive':'not identified by table metadata'})
(r/'export-contract.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'tables':results,'common':len(common),'Windows_only_count':len(n.keys()-w.keys()),'Wine_only_count':len(w.keys()-n.keys()),'conclusions':out['conclusions']},indent=2))
