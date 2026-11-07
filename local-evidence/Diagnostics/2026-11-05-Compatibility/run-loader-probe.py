#!/usr/bin/env python3
"""Run only the standalone probe via offline UMU/CachyOS in a dedicated prefix.

The experimental FiveM directory is exposed read-only. No Heroic game/account
entry is used. Logs remain private. This does not run FiveM or CreateComponent.
"""
from pathlib import Path
import argparse
import json
import os
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
project = root.parents[1]
private = root / 'private'
private.mkdir(mode=0o700, exist_ok=True)
private.chmod(0o700)
run = private / 'api-probe-cachyos'
run.mkdir(mode=0o700, exist_ok=True)
prefix = run / 'prefix'
assert prefix.is_relative_to(private) and prefix != Path.home()
parser = argparse.ArgumentParser(description=__doc__)
selection = parser.add_mutually_exclusive_group()
selection.add_argument('--adhesive', action='store_true')
selection.add_argument('--adhesive-initialized', action='store_true')
selection.add_argument('--seh-hook', action='store_true')
parser.add_argument('--tag', default='')
options = parser.parse_args()
assert all(c.isalnum() or c == '-' for c in options.tag)
mode = ['--adhesive-initialized'] if options.adhesive_initialized else (['--adhesive'] if options.adhesive else [])
label = 'seh-hook' if options.seh_hook else ('adhesive-initialized' if options.adhesive_initialized else ('adhesive' if mode else 'abi'))
if options.tag:
    label += '-' + options.tag
log = run / (label + '.log')
assert not log.exists(), 'Preserve earlier test logs; select a new log name for a new test.'
heroic = Path.home() / '.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
runner = heroic / 'tools/proton/Proton-CachyOS-latest'
umu = heroic / 'tools/runtimes/umu/umu-run'
args = [
    'flatpak', 'run', '--filesystem=' + str(root),
    '--filesystem=' + str(project / 'Run-Adhesive-Test') + ':ro',
    '--unshare=network',
    '--env=WINEPREFIX=' + str(prefix),
    '--env=PROTONPATH=' + str(runner),
    '--env=GAMEID=umu-default', '--env=UMU_RUNTIME_UPDATE=0',
    '--env=PROTONFIXES_DISABLE=1', '--env=PROTON_USE_PIPEWIRE=0',
    '--env=PROTON_FSR4_UPGRADE=0',
    '--env=WINEDLLOVERRIDES=winemenubuilder.exe=d',
    '--env=WINEDEBUG=' + ('+seh,+module' if mode else '-all'),
    '--command=' + str(umu), 'com.heroicgameslauncher.hgl',
    str(root / ('seh-hook-probe.exe' if options.seh_hook else 'loader-probe.exe')), *mode,
]
started = time.monotonic()
timed_out = False
with log.open('xb') as output:
    log.chmod(0o600)
    child = subprocess.Popen(args, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        code = child.wait(timeout=55)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(child.pid, signal.SIGTERM)
        try:
            code = child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            code = child.wait()
result = {'mode': label, 'returncode': code, 'timed_out': timed_out,
          'elapsed_seconds': round(time.monotonic() - started, 2),
          'log_bytes': log.stat().st_size, 'network': 'flatpak --unshare=network',
          'runtime_directory': 'read-only Flatpak filesystem grant',
          'runner': str(runner), 'prefix': str(prefix)}
result_name = 'compat-probe-seh-hook.txt' if options.seh_hook else ('compat-probe-adhesive-initialized.txt' if options.adhesive_initialized else ('compat-probe-adhesive.txt' if mode else 'compat-probe-abi.txt'))
result_file = prefix / 'drive_c' / result_name
result['probe_result_file_exists'] = result_file.is_file()
if result_file.is_file():
    lines = result_file.read_text(errors='replace').splitlines()
    result['probe_result_markers'] = [s for s in lines if s.startswith(('ABI_RESULT=', 'LOAD_RESULT=', 'HOOK_RESULT=', 'PROBE_EXIT_CODE=', 'LoadLibraryExW_error=', 'exception_count=', 'loader_exception_count='))]
summary = run / (label + '-summary.json')
summary.write_text(json.dumps(result, indent=2) + '\n')
summary.chmod(0o600)
print(json.dumps(result))
sys.exit(code if not timed_out else 124)
