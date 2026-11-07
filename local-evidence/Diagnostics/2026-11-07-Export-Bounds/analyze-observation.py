#!/usr/bin/env python3
"""Analyze only the completed initializer-thread run; reject partial tool runs."""
from pathlib import Path
import argparse,collections,hashlib,json,re
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tag',default='fullhost-primary-only');p.add_argument('--output',default='evidence.json');o=p.parse_args()
assert o.tag and all(c.isalnum() or c=='-' for c in o.tag)
assert Path(o.output).name==o.output and o.output.endswith('.json')
run=r/'private'/o.tag;text=(run/'export-resolver-observer.txt').read_text();lines=text.splitlines()
fields={s.split('=',1)[0]:int(s.split('=',1)[1],16) for s in lines if re.fullmatch(r'[A-Z0-9_]+=0x[0-9a-f]+',s)}
assert 'OBSERVER_COMPLETE' in lines and fields['OBSERVER_ERRORS']==0 and fields['CAPTURED_AV']==1
assert fields['FAULT_RVA']==0xd9fec5 and fields['FIRST_LOOKUPS']==1 and fields['FIRST_INDEX']==0
assert fields['NUMBER_OF_NAMES']==1468 and fields['PRIMARY_THREAD_ONLY']==fields['INITIALIZER_THREAD']
assert fields['NTDLL_RESOLVE_CALLS']==fields['NTDLL_RESOLVE_RETURNS']
cut=next(i for i,s in enumerate(lines) if s=='EXCEPTION=0x00000000c0000005')
start=next(i for i,s in enumerate(lines) if s.startswith('COPIED_COUNT_WATCH='))
pending=collections.defaultdict(list);pairs=[]
for s in lines[:cut]:
 if s.startswith('RESOLVE_CALL '):
  f=dict(re.findall(r'(\w+)=([^ ]+)',s));pending[f['tid']].append(f)
 elif s.startswith('RESOLVE_RETURN '):
  f=dict(re.findall(r'(\w+)=([^ ]+)',s));a=pending[f['tid']].pop();assert a['name']==f['name'] and a['api']==f['api']
  value=int(f['value'],16);pairs.append(dict(api=f['api'],name=f['name'],caller=a['caller'],initiator=f['initiator'],value=hex(value),failed=(value!=0 if f['api']=='NT' else value==0)))
assert all(not s for s in pending.values())
fail=[f for f in pairs if f['failed']]
counts=collections.Counter(f['api'] for f in pairs)
logs='\n'.join(p.read_text(errors='replace') for p in run.glob('CitizenFX_log*'))
assert 'Adhesive failed to load under Wine (error 998)' in logs
summary=json.loads((run/'summary.json').read_text());assert summary['files_unchanged']
out=dict(tag=o.tag,trace_sha256=hashlib.sha256((run/'export-resolver-observer.txt').read_bytes()).hexdigest(),
 completed_at_original_fault=True,fault_RVA='0xd9fec5',loader_error=998,
 scope={'public_functions':['kernel32!GetProcAddress','ntdll!LdrGetProcedureAddress'],
 'thread':'primary/observed DLL_PROCESS_ATTACH thread',
 'count_watch_window':'first lookup index0 through first access violation',
 'count_watch_address_field':'copied NTDLL IMAGE_EXPORT_DIRECTORY.NumberOfNames',
 'other_threads_or_custom_resolvers':'not claimed to be covered'},
 visible_caller_label_is_not_a_complete_call_stack=True,
 pre_AV_interface_level_pairs=len(pairs),pre_AV_pairs_by_interface=dict(counts),
 pre_AV_failed_interface_returns=fail,
 pre_AV_Adhesive_initiated_observed_requests=sum(f['initiator']=='adhesive.dll' for f in pairs),
 observed_resolver_events_during_walk=sum(s.startswith('RESOLVE_') for s in lines[start:cut]),
 observed_count_accesses_during_walk=sum(s.startswith('COUNT_ACCESS ') for s in lines[start:cut]),
 declared_names_at_first_lookup=1468,observer_errors=0,
 meaning='No observed standard-resolver failure from Adhesive identifies its manual-search target. The observed initializer thread does not reaccess this count field during the walk.',
 does_not_prove=['No missing Windows API is required by the private resolver.','The count was never cached before lookup0.','A cached bound was absent or not compared.','All TLS or ABI behavior is correct.'],
 patches_to_Wine_FiveM_or_Adhesive=False,
 runtime_hashes=summary['hashes'],all_pre_AV_pairs=pairs)
if 'FAULT_INDEX' in fields:
 assert fields['FAULT_INDEX']==1477 and fields['FAULT_NAME_RVA']==0x130012
 assert fields['FAULT_BUFFER']==fields['BUFFER_BASE']
 assert fields['COUNT_AT_AV']==fields['NUMBER_OF_NAMES']==1468
 assert fields['WATCH_AT_AV']==fields['COPIED_COUNT_WATCH']
 assert fields['DR7_AT_AV']&64 and ((fields['DR7_AT_AV']>>28)&15)==15
 assert fields['NUMBER_OF_FUNCTIONS']==1468 and fields['ADDRESS_OF_NAMES']==0xcb718 and fields['ADDRESS_OF_ORDINALS']==0xcce08
 out['fault_audit']={'index':1477,'name_RVA':'0x130012','same_buffer_as_first_lookup':True,
  'NumberOfNames_still_1468_at_fault':True,'read_write_4byte_watch_still_enabled_at_fault':True,
  'count_accesses_on_observed_thread_during_walk':out['observed_count_accesses_during_walk']}
(r/o.output).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['all_pre_AV_pairs','runtime_hashes']},indent=2))
