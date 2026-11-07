#!/usr/bin/env python3
"""Temporarily select the experimental CoreRT in DIAGNOSTIC fullhost only."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
root=Path(__file__).resolve().parent;project=root.parents[1]
artifact=root/'artifact';runtime=project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost'
validation=json.loads((artifact/'validation.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert validation['sha256']==digest(artifact/'CoreRT.dll')
assert validation['pdb_matches'] and validation['windows_loader_smoke']=='passed'
assert validation['source_sha256']['code/client/citicore/DllGameComponent.Win32.cpp']==digest(root/'source/DllGameComponent.Win32.cpp')
assert digest(runtime/'adhesive.dll')=='3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b'
items=[(runtime/'CoreRT.dll',artifact/'CoreRT.dll'),(runtime/'dbg/CoreRT.pdb',artifact/'CoreRT.pdb')]
assert runtime.resolve().is_relative_to(project/'Diagnostics')
old={str(dest):os.readlink(dest) for dest,_ in items if dest.is_symlink()};assert len(old)==2
backup=root/'artifact-link-backup.json';assert not backup.exists();backup.write_text(json.dumps(old,indent=2)+'\n')
try:
 for dest,target in items:
  staged=dest.with_name(dest.name+'.direct-repair-new');assert not staged.exists();staged.symlink_to(target);os.replace(staged,dest)
 code=subprocess.call([sys.executable,str(root/'run-direct.py'),'--tag','fullhost-core-experiment','--legacy-ui'])
finally:
 for dest,_ in items:
  staged=dest.with_name(dest.name+'.direct-repair-restore');assert not staged.exists();staged.symlink_to(old[str(dest)]);os.replace(staged,dest)
 restored=all(os.readlink(dest)==old[str(dest)] for dest,_ in items)
 (root/'artifact-link-restoration.json').write_text(json.dumps({'restored':restored,'restored_core_sha256':digest(runtime/'CoreRT.dll'),'official_adhesive_sha256':digest(runtime/'adhesive.dll')},indent=2)+'\n');assert restored
print('Diagnostic CoreRT and PDB links restored; original runtime directories untouched.')
raise SystemExit(code)
