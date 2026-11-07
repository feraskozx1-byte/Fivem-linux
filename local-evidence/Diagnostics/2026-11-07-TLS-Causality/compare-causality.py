#!/usr/bin/env python3
"""Compare completed before/after traces without executing any Windows program."""
from pathlib import Path
import argparse,collections,hashlib,json,re
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--before',default='adhesive-direct-baseline');p.add_argument('--after',default='adhesive-direct-prototype')
p.add_argument('--output',default='causality-comparison.json');opt=p.parse_args()
assert all(s and all(c.isalnum() or c=='-' for c in s) for s in [opt.before,opt.after])
assert Path(opt.output).name==opt.output and opt.output.endswith('.json')
def collect(tag):
 p=r/'private'/tag
 lines=(p/'tls-api-observer.txt').read_text().splitlines()
 summary=json.loads((p/'summary.json').read_text())
 values={s.split('=',1)[0]:int(s.split('=',1)[1],16) for s in lines
         if re.fullmatch(r'[A-Z_]+=0x[0-9a-f]+',s)}
 assert values['OBSERVER_ERRORS']==values['PRODUCER_MISMATCHES']==0
 assert values['CAPTURED_AV']==1 and values['API_CALLS']==values['API_RETURNS']
 assert values['ADHESIVE_EXCEPTION_RVA']==0xd9fec5 and summary['files_unchanged']
 av=next(i for i,s in enumerate(lines) if s.startswith('EXCEPTION=0x00000000c0000005'))
 before=lines[:av]
 calls=[];pending={}
 for s in before:
  if s.startswith('NT_CALL '):
   f=dict(re.findall(r'(\w+)=([^ ]+)',s));assert f['tid'] not in pending;pending[f['tid']]=f
  elif s.startswith('NT_RETURN '):
   f=dict(re.findall(r'(\w+)=([^ ]+)',s));c=pending.pop(f['tid'])
   assert c['module']==f['module'];calls.append((c['module'],c['caller'],int(f['status'],16)))
 assert not pending
 consumers=[int(s.split('=')[1],16) for s in before if s.startswith('CONSUMER index=')]
 producer_rows=[]
 for s in before:
  if s.startswith('PRODUCER '):
   f=dict(re.findall(r'(\w+)=(0x[0-9a-f]+)',s));f={k:int(v,16) for k,v in f.items()}
   assert f['previous']==f['r13'] and f['next']==f['previous']+1
   producer_rows.append(f)
 logs='\n'.join(f.read_text(errors='replace') for f in p.glob('CitizenFX_log*'))
 assert 'Adhesive failed to load under Wine (error 998)' in logs
 return dict(tag=tag,source=p.relative_to(r).as_posix(),
   trace_sha256=hashlib.sha256((p/'tls-api-observer.txt').read_bytes()).hexdigest(),
   observer_complete=True,runner_stop_reason=summary['stop_reason'],
   runner_returncode=summary['runner_returncode'],
   branch_encoding_hex=f"{values['NTDLL_STATIC_TLS_BRANCH']:04x}",
   counters={k:values[k] for k in ['API_CALLS','API_RETURNS','NONZERO_API_RETURNS','LOOKUPS','PRODUCERS','PRODUCER_MISMATCHES','OBSERVER_ERRORS']},
   before_AV=dict(paired_calls=len(calls),nonzero_returns=sum(t[2]!=0 for t in calls),
    Adhesive_module_calls=sum(t[0]=='adhesive.dll' for t in calls),
    Adhesive_direct_caller_calls=sum(t[1]=='adhesive.dll' for t in calls),
    calls=[dict(module=t[0],caller=t[1],status=hex(t[2])) for t in calls]),
   logged_consumers=consumers,logged_producers=producer_rows,
   fault_RVA=hex(values['ADHESIVE_EXCEPTION_RVA']),loader_error=998,
   hashes=summary['hashes'],files_unchanged=summary['files_unchanged'])
a=collect(opt.before);b=collect(opt.after)
assert a['branch_encoding_hex']=='2674' and b['branch_encoding_hex']=='0774'
assert a['hashes']==b['hashes']
assert [(c['module'],c['caller']) for c in a['before_AV']['calls']]==[(c['module'],c['caller']) for c in b['before_AV']['calls']]
assert a['before_AV']['nonzero_returns']>0 and b['before_AV']['nonzero_returns']==0
assert a['logged_consumers']==b['logged_consumers'] and a['logged_producers']==b['logged_producers']
assert b['counters']['LOOKUPS']==1478 and b['counters']['PRODUCERS']==1477
out=dict(before=a,after=b,conclusion={
 'public_API_intervention_verified_in_executing_NTDLL':True,
 'all_nonzero_callout_statuses_removed':True,
 'same_pre_AV_modules_and_callers_in_same_order':True,
 'same_index_production_and_fault':True,
 'DisableThreadLibraryCalls_return_difference_explains_this_failure':False,
 'all_possible_TLS_defects_excluded':False,
 'Adhesive_loaded_successfully':False,
 'Wine_prototype_is_Adhesive_fix':False,
 'next_gap':'Identity of the unresolved NTDLL export and supported not-found path; 1477 is a repeated previous-index + 1, not a fixed initial Windows ordinal.'})
(r/opt.output).write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k=='conclusion'},indent=2))
print('Before/after pre-AV pairs:',a['before_AV']['paired_calls'],b['before_AV']['paired_calls'])
print('Before/after pre-AV nonzero returns:',a['before_AV']['nonzero_returns'],b['before_AV']['nonzero_returns'])
