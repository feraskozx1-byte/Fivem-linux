#!/usr/bin/env python3
"""Expose the tested public Wine prototype in a child mount namespace only."""
from pathlib import Path
import hashlib,json,os,sys
r=Path(__file__).resolve().parent
p=r.parents[1]/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32/ntdll.dll'
m=json.loads((r/'private/wine-prototype/build.json').read_text())
original=Path(m['original_path']);prototype=r/'private/wine-prototype/ntdll.dll'
assert hashlib.sha256(original.read_bytes()).hexdigest()==m['original_sha256']
assert not p.is_symlink(), 'Do not substitute an unknown prefix configuration'
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['original_sha256']
assert hashlib.sha256(prototype.read_bytes()).hexdigest()==m['prototype_sha256']
assert sys.argv[1:], 'Supply an existing test command'
# Also mount over the *diagnostic* prefix file so PE disk reads and executable
# mapping agree. Mounts are private and read-only; no file on disk is replaced.
args=['bwrap','--die-with-parent','--dev-bind','/','/',
      '--ro-bind',str(prototype),str(original),
      '--ro-bind',str(prototype),str(p),'--',*sys.argv[1:]]
os.execvp(args[0],args)
