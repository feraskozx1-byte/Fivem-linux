from pathlib import Path
import argparse,hashlib,json,re
a=argparse.ArgumentParser();a.add_argument('--tag',default='api-observer-positive');opt=a.parse_args()
assert opt.tag and all(c.isalnum() or c=='-' for c in opt.tag)
r=Path(__file__).resolve().parent;p=r/'private'/opt.tag
s=(p/'tls-api-observer.txt').read_text()
assert 'OBSERVER_ERRORS=0x0000000000000000' in s and 'CHILD_EXIT=0x0000000000000000' in s
assert s.count('module=tls-fixture.dll status=0x00000000c0000135')==2
assert s.count('module=tls-control.dll status=0x0000000000000000')==1
assert 'RESULT=PASS' in (p/'fixture-result.txt').read_text()
out={'passed':True,'source_sha256':hashlib.sha256((r/'api-observer.c').read_bytes()).hexdigest(),'host_observer_sha256':hashlib.sha256((r/'api-observer-host.exe').read_bytes()).hexdigest(),'positive_static_TLS_failure_returns':2,'positive_no_TLS_success_returns':1,'NT_entry_and_return_monitor_validated':True}
(r/'api-observer-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
