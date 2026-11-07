#!/usr/bin/env python3
"""Offline, bounded Adhesive initialization comparison; uses diagnostic prefix only."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import time

root = Path(__file__).resolve().parent
project = root.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('core', choices=['old', 'new'])
parser.add_argument('--tag', required=True)
parser.add_argument('--native-msvcp', action='store_true')
parser.add_argument('--native-ucrt', action='store_true')
opt = parser.parse_args()
if not opt.tag or not all(c.isalnum() or c == '-' for c in opt.tag):
    parser.error('tag must be alphanumeric with optional hyphens')
private = root / 'private'
private.mkdir(mode=0o700, exist_ok=True)
private.chmod(0o700)
run = private / (opt.core + '-' + opt.tag)
run.mkdir(mode=0o700)  # refuse overwriting evidence
# Reuse only the established account-free diagnostic prefix, without copying it.
prefix = project / 'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
assert prefix.is_dir() and prefix.is_relative_to(project / 'Diagnostics')
result = prefix / ('drive_c/adhesive-probe-v4-' + opt.core + '-core.txt')
if result.exists():
    result.rename(run / 'previous-prefix-result.txt')
heroic = Path.home() / '.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
runner = heroic / 'tools/proton/Proton-CachyOS-latest'
umu = heroic / 'tools/runtimes/umu/umu-run'
args = ['flatpak', 'run', '--filesystem=' + str(root),
        '--filesystem=' + str(prefix),
        '--filesystem=' + str(project / 'Run-Adhesive-Test') + ':ro',
        '--filesystem=' + str(project / 'Run-CoreRT-Test') + ':ro',
        '--unshare=network', '--env=WINEPREFIX=' + str(prefix),
        '--env=PROTONPATH=' + str(runner), '--env=GAMEID=umu-default',
        '--env=UMU_RUNTIME_UPDATE=0', '--env=PROTONFIXES_DISABLE=1',
        '--env=PROTON_USE_PIPEWIRE=0', '--env=PROTON_FSR4_UPGRADE=0',
        '--env=WINEDLLOVERRIDES=winemenubuilder.exe=d' + (';msvcp140,vcruntime140,vcruntime140_1=n' if opt.native_msvcp else '') + (';ucrtbase=n' if opt.native_ucrt else ''),
        '--env=WINEDEBUG=+seh,+module', '--command=' + str(umu),
        'com.heroicgameslauncher.hgl', str(root / 'loader-probe.exe'), '--' + opt.core + '-core']

def limits():
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024 * 1024, 8 * 1024 * 1024))

start = time.monotonic()
timed_out = False
with (run / 'wine.log').open('xb') as log:
    proc = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True, preexec_fn=limits)
    try:
        code = proc.wait(timeout=55)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            code = proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            code = proc.wait()
data = result.read_bytes() if result.exists() else b''
if data:
    (run / 'probe-result.txt').write_bytes(data)
    # The next run must create a fresh result. Preserve this one in its run folder.
    result.unlink()
summary = dict(core=opt.core, tag=opt.tag, native_msvcp=opt.native_msvcp, native_ucrt=opt.native_ucrt,
               returncode=code, timed_out=timed_out,
               elapsed_seconds=round(time.monotonic()-start, 2),
               log_bytes=(run / 'wine.log').stat().st_size,
               network='disabled by Flatpak', prefix=str(prefix),
               probe_sha256=hashlib.sha256((root/'loader-probe.exe').read_bytes()).hexdigest(),
               markers=[s for s in data.decode(errors='replace').splitlines()
                        if s.startswith(('MODE=', 'preload_core_error=', 'core_exception_count=',
                                         'resolved_core_path=', 'VEH ', 'LoadLibraryExW_error=',
                                         'LOAD_RESULT=', 'PROBE_EXIT_CODE='))])
(run / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))
raise SystemExit(code if not timed_out else 124)
