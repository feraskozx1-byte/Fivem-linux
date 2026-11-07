from pathlib import Path
import argparse,hashlib,json,re
r=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);o=p.parse_args()
assert o.tag and all(c.isalnum() or c=='-' for c in o.tag)
run=r/'private'/o.tag;s=(run/'export-resolver-observer.txt').read_text()
assert 'OBSERVER_COMPLETE' in s and 'OBSERVER_ERRORS=0x0000000000000000' in s
assert 'CHILD_EXIT=0x0000000000000000' in s and 'COUNT_ACCESSES=0x0000000000000004' in s
assert s.count('COUNT_ACCESS ')==4 and s.count('RESOLVE_RETURN ')==10
assert s.count('value=0x00000000c000007a')==3
assert s.count('api=Win32 name=CodexAbsentExport_20261107 value=0x0000000000000000')==1
assert s.count('api=Win32 name=ntclose value=0x0000000000000000')==1
assert 'MONITOR_CONTINUITY_LOST' not in s
fixture=(run/'export-fixture.txt').read_text();assert fixture.count('PASS ')==8 and 'FAIL' not in fixture and 'RESULT=PASS' in fixture
out={'passed':True,'source_sha256':hashlib.sha256((r/'resolver-observer.c').read_bytes()).hexdigest(),
 'host_observer_sha256':hashlib.sha256((r/'resolver-observer-host.exe').read_bytes()).hexdigest(),
 'fixture_exe_sha256':hashlib.sha256((r/'resolver-fixture.exe').read_bytes()).hexdigest(),
 'fixture_tag':o.tag,'checks':8,'observed_paired_resolutions':10,'expected_count_reads_observed':4,
 'static_TLS_test':False,'Windows_native_run_this_stage':False}
(r/'observer-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
