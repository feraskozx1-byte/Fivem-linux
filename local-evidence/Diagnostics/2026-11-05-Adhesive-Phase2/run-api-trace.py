#!/usr/bin/env python3
"""Temporarily enable Wine's own filtered public-API trace in diagnostic prefix.

This changes logging configuration only; no import results, exceptions, Wine
identity or security decisions are overridden. No existing product files change.
Run sequentially with other diagnostic-prefix tools.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parent
project = root.parents[1]
prefix = project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
registry = prefix/'user.reg'
assert registry.resolve().is_relative_to(project/'Diagnostics') and not registry.is_symlink()
tag = sys.argv[1] if len(sys.argv)==2 else 'fullhost-public-api'
assert tag and all(c.isalnum() or c=='-' for c in tag)
backup = root/'private'/('registry-backup-'+tag)
backup.mkdir(mode=0o700)
original = registry.read_bytes()
(backup/'user.reg.before').write_bytes(original)
section = '[Software\\\\Wine\\\\Debug]'
text = original.decode('utf-8')
new_section = section+' 0\n"RelayFromInclude"="adhesive.dll"\n\n'
if section in text:
    start = text.index(section)
    end = text.find('\n[',start+len(section))
    if end<0:
        end = len(text)
    # Replace the inspected Wine default exclusions: FromExclude has priority
    # over FromInclude. The entire original registry is backed up/restored.
    current = text[start:end]
    assert '"RelayFromInclude"=' not in current, 'Preserve any custom prior include filter'
    configured = text[:start]+new_section+text[end:]
else:
    configured = text+'\n'+new_section
try:
    registry.write_text(configured)
    code = subprocess.call([sys.executable,str(root/'run-fullhost.py'),'--tag',tag,'--legacy-ui','--relay-trace'])
finally:
    registry.write_bytes(original)
    restored = registry.read_bytes()==original
    (backup/'restoration.json').write_text(json.dumps(dict(restored=restored,
        user_reg_sha256_before=hashlib.sha256(original).hexdigest(),
        user_reg_sha256_after=hashlib.sha256(registry.read_bytes()).hexdigest()),indent=2)+'\n')
    assert restored
print('Diagnostic user.reg restored exactly; filter affected logging only.')
raise SystemExit(code)
