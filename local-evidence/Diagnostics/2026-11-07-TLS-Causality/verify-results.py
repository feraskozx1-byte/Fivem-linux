#!/usr/bin/env python3
"""Verify saved fixture results, native PE identity, and restoration; no execution."""
from pathlib import Path
import hashlib,json,re,subprocess
r=Path(__file__).resolve().parent;project=r.parents[1]
def values(s):
 return dict(line.split('=',1) for line in s.splitlines() if line.startswith((
  'LdrDisableThreadCalloutsForDll-static-status=',
  'DisableThreadLibraryCalls-static-return=',
  'DisableThreadLibraryCalls-control-return=')))
fixtures=[]
for year,baseline in [('2022','win2022-warm-retry'),('2025','win2025-binary')]:
 ref=r/'private'/('reference-'+year)
 native=(ref/'native/tls-result.txt').read_text(encoding='utf-8-sig')
 hashes=json.loads((ref/'native/hashes.json').read_text(encoding='utf-8-sig'))
 pe={f:hashlib.sha256((ref/'bin'/f).read_bytes()).hexdigest() for f in ['tls-test.exe','tls-fixture.dll','tls-control.dll']}
 native_hashes={a['name']:a['sha256'].lower() for a in hashes}
 assert all(native_hashes[n]==h for n,h in pe.items())
 assert native.count('PASS ')==29 and 'RESULT=PASS' in native
 results={}
 for tag in [baseline,'prototype-direct-win'+year]:
  p=r/'private'/tag;s=json.loads((p/'summary.json').read_text());text=(p/'results.txt').read_text()
  assert s['hashes']==pe and s['success'] and s['pass_count']==29 and s['fail_count']==0
  if tag.startswith('prototype'):assert values(text)==values(native)
  else:assert values(text)['LdrDisableThreadCalloutsForDll-static-status']=='0x00000000c0000135'
  assert [l for l in text.splitlines() if l.startswith('OBS ')]==[l for l in native.splitlines() if l.startswith('OBS ')]
  results[tag]={'checks':29,'native_API_returns_match':values(text)==values(native)}
 # No-TLS control must have no PE TLS directory, rather than a tiny TLS object.
 b=(ref/'bin/tls-control.dll').read_bytes();peoff=int.from_bytes(b[60:64],'little');opt=peoff+24
 assert b[opt+112+72:opt+112+80]==b'\0'*8
 fixtures.append({'Windows':year,'same_PE_hashes':pe,'no_TLS_control_has_no_TLS_directory':True,'native_checks':29,'Wine_runs':results})
m=json.loads((r/'private/wine-prototype/build.json').read_text())
restored={}
for name,p,expected in [
 ('installed_Proton_NTDLL',Path(m['original_path']),m['original_sha256']),
 ('diagnostic_prefix_NTDLL',project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32/ntdll.dll',m['original_sha256']),
 ('official_Adhesive',project/'Official-Reference/adhesive-24769.dll','3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b'),
 ('running_Adhesive',project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost/adhesive.dll','3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b')]:
 digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==expected;restored[name]=digest
s=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/dosdevices/s:'
assert s.is_symlink() and str(s.readlink())=='/home/feras'
assert (project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost/CoreRT.dll').resolve()==(project/'Run-CoreRT-Test/CoreRT.dll').resolve()
restored['S_mapping']=str(s.readlink())
baseline=json.loads((project/'Diagnostics/2026-11-05-Adhesive-RCA/Index-Origin/preservation.json').read_text())
status=subprocess.check_output(['git','status','--short'],cwd=project/'Original-PR4050-Source',text=True)
# Record the existing source changes; this stage intentionally makes none there.
restored['original_source_git_status']=status
assert status==baseline['original_git_status']
loader=project/'Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp'
assert loader.read_bytes()==(project/'Diagnostics/2026-11-05-Adhesive-Direct-Repair/DllGameComponent.before.bak').read_bytes()
restore_result=json.loads((r/'private/restored-direct-win2022/summary.json').read_text())
assert restore_result['success'] and restore_result['pass_count']==29
assert restore_result['public_API_values']['LdrDisableThreadCalloutsForDll-static-status']=='0x00000000c0000135'
out={'verified':True,'fixtures':fixtures,'restoration':restored,
 'unpatched_API_behavior_reproduced_after_mount_exit':True,
 'prototype_is_not_installed':True,'native_CI_run':42379209634,
 'native_source_commit':'5d2947dbdf536734d205171804f47d9272aca5e8'}
(r/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('Verified both native/Wine PE pairs, 29 checks per run, prototype API results, no-TLS control, official hashes, and restoration.')
