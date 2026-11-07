#!/usr/bin/env python3
"""Test existing Microsoft VC++ DLLs in diagnostic prefix, restoring every file."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
project = root.parents[1]
source = Path.home() / 'Games/FiveM-Official-Test/GTA-Prefix-Work/drive_c/windows/system32'
target = project / 'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32'
assert target.is_relative_to(project / 'Diagnostics')
expected = {
    'msvcp140.dll': '0f885b509a685d2bbfa652fed26b5fb31d88fbdab0a978c641d1c7b8aa460aa9',
    'vcruntime140.dll': 'd5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066',
    'vcruntime140_1.dll': '1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f',
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('tag')
parser.add_argument('--ucrt', action='store_true')
opt = parser.parse_args()
tag = opt.tag
if opt.ucrt:
    expected['ucrtbase.dll'] = '51cbbde17a768930300236facd9738f54b7801e6715771ff8af90bfbe3fad44f'
if not tag or not all(c.isalnum() or c == '-' for c in tag):
    raise SystemExit('invalid tag')
backup = root / 'private' / ('runtime-backup-' + tag)
backup.mkdir(mode=0o700)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
for name, want in expected.items():
    assert digest(source / name) == want, name + ' source hash changed'
before = {name: digest(target / name) if (target / name).exists() else None for name in expected}
(backup / 'before.json').write_text(json.dumps(before, indent=2)+'\n')
replaced = []
try:
    for name in expected:
        dest = target / name
        staged = backup / (name + '.staged')
        shutil.copy2(source / name, staged)  # < 0.8 MB total; source remains read-only
        if dest.exists() or dest.is_symlink():
            os.replace(dest, backup / name)  # preserve symlink or hardlink intact
        replaced.append(name)
        os.replace(staged, dest)
    code = subprocess.call([sys.executable, str(root / 'run-probe.py'), 'new', '--tag', tag, '--native-msvcp'] + (['--native-ucrt'] if opt.ucrt else []))
finally:
    for name in reversed(replaced):
        dest = target / name
        if (backup / name).exists() or (backup / name).is_symlink():
            os.replace(backup / name, dest)
        else:
            dest.unlink(missing_ok=True)
    after = {name: digest(target / name) if (target / name).exists() else None for name in expected}
    (backup / 'restoration.json').write_text(json.dumps(dict(before=before, after=after, restored=before == after), indent=2)+'\n')
    assert before == after, 'diagnostic runtime restoration mismatch'
print('Diagnostic-prefix VC++ files restored; main prefix untouched.')
raise SystemExit(code)
