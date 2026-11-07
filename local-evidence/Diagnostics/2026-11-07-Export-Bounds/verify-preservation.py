#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
r=Path(__file__).resolve().parent;project=r.parents[1]
before=json.loads((project/'Diagnostics/2026-11-05-Adhesive-RCA/Index-Origin/preservation.json').read_text())
status=subprocess.check_output(['git','status','--short'],cwd=project/'Original-PR4050-Source',text=True)
assert status==before['original_git_status']
assert (project/'Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp').read_bytes()==(project/'Diagnostics/2026-11-05-Adhesive-Direct-Repair/DllGameComponent.before.bak').read_bytes()
expected={
 'Official-Reference/adhesive-24769.dll':'3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b',
 'Run-Adhesive-Test/adhesive.dll':'3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b',
 'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost/adhesive.dll':'3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b',
 'Run-CoreRT-Test/CoreRT.dll':'cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64',
 'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32/ntdll.dll':'af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5'}
hashes={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in expected};assert hashes==expected
proton=Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/tools/proton/Proton-CachyOS-latest/files/lib/wine/x86_64-windows/ntdll.dll'
assert hashlib.sha256(proton.read_bytes()).hexdigest()=='af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5'
prefix=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
s=prefix/'dosdevices/s:';assert s.is_symlink() and str(s.readlink())=='/home/feras'
assert (project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost/CoreRT.dll').resolve()==(project/'Run-CoreRT-Test/CoreRT.dll').resolve()
for name in ['export-fixture.txt','export-resolver-observer.txt']:assert not (prefix/'drive_c'/name).exists()
validation=json.loads((r/'private/fullhost-fault-audit/observer-build-validation.json').read_text())
assert validation['passed'] and validation['source_sha256']==hashlib.sha256((r/'resolver-observer.c').read_bytes()).hexdigest()
assert validation['host_observer_sha256']==hashlib.sha256((r/'resolver-observer-host.exe').read_bytes()).hexdigest()
summary=json.loads((r/'private/fullhost-fault-audit/summary.json').read_text());assert summary['files_unchanged'] and summary['network']=='disabled'
out={'verified':True,'hashes':hashes,'original_source_git_status_unchanged':True,'original_loader_source_unchanged':True,
 'installed_Proton_NTDLL_unmodified':True,'CoreRT_link_unchanged':True,'S_mapping_restored':True,
 'diagnostic_snapshots_archived':True,'final_observer_source_and_binary_match_validated_build':True,
 'main_prefix_used':False,'TLS_tests_repeated':False,'runtime_or_Wine_patch_installed':False,
 'new_directory_file_bytes':sum(p.stat().st_size for p in r.rglob('*') if p.is_file())}
(r/'preservation.json').write_text(json.dumps(out,indent=2)+'\n')
print('Verified original DLLs, source status, unmodified Wine, validated observer build, and diagnostic-prefix cleanup.')
