#!/usr/bin/env python3
"""Run the real local FiveM host offline until Adhesive's loader outcome.

No component code is injected or patched. Sources are exposed read-only; only
the prepared diagnostic runtime and existing account-free diagnostic prefix
are writable. This is not a game or connection test.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import time

root = Path(__file__).resolve().parent
project = root.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tag', required=True)
parser.add_argument('--legacy-ui', action='store_true', help='Existing CitizenFX_NoTenUI setting; updater presentation only')
parser.add_argument('--virtual-trace', action='store_true', help='Additional Wine virtual-memory lifecycle diagnostics')
parser.add_argument('--relay-trace', action='store_true', help='Use only through run-api-trace.py, which installs/restores the diagnostic filter')
opt = parser.parse_args()
if not opt.tag or not all(c.isalnum() or c == '-' for c in opt.tag):
    parser.error('tag must contain letters/numbers/hyphens only')
runtime = project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost'
assert (runtime/'FiveM.exe').is_file() and not (runtime/'FiveM.exe').is_symlink()
prefix = project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
assert prefix.is_dir() and prefix.is_relative_to(project/'Diagnostics')
run = root/'private'/opt.tag
run.mkdir(mode=0o700)
heroic = Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
proton = heroic/'tools/proton/Proton-CachyOS-latest'
umu = heroic/'tools/runtimes/umu/umu-run'
game = Path.home()/'Games/Heroic/GTAV'
args = ['flatpak', 'run', '--filesystem='+str(root), '--filesystem='+str(prefix), '--filesystem='+str(runtime),
        '--nofilesystem='+str(Path.home()/'Games/FiveM-Official-Test'),
        '--filesystem='+str(root/'artifact')+':ro',
        '--filesystem='+str(project/'Run-CoreRT-Test')+':ro',
        '--filesystem='+str(project/'Run-Adhesive-Test')+':ro',
        '--filesystem='+str(project/'Diagnostics/2026-11-05-Compatibility/ci-citicore/downloaded-build/citicore-x64-42019993897')+':ro',
        '--filesystem='+str(game)+':ro', '--unshare=network',
        '--env=WINEPREFIX='+str(prefix), '--env=PROTONPATH='+str(proton),
        '--env=GAMEID=umu-default', '--env=UMU_RUNTIME_UPDATE=0',
        '--env=PROTONFIXES_DISABLE=1', '--env=PROTON_USE_PIPEWIRE=0',
        '--env=PROTON_FSR4_UPGRADE=0', '--env=WINEDLLOVERRIDES=winemenubuilder.exe=d',
        '--env=WINEDEBUG=+pid,+seh,+module,+file', '--command='+str(umu),
        'com.heroicgameslauncher.hgl', str(runtime/'FiveM.exe')]
if opt.legacy_ui:
    args.insert(args.index('--env=WINEDEBUG=+pid,+seh,+module,+file'), '--env=CitizenFX_NoTenUI=1')
if opt.virtual_trace:
    args[args.index('--env=WINEDEBUG=+pid,+seh,+module,+file')] += ',+virtual'
if opt.relay_trace:
    assert not opt.virtual_trace, 'Keep expensive debug dimensions separate'
    assert '"RelayFromInclude"="adhesive.dll"' in (prefix/'user.reg').read_text()
    args[args.index('--env=WINEDEBUG=+pid,+seh,+module,+file')] += ',+relay'
existing_logs = set((runtime/'logs').glob('*'))
start = time.monotonic()
deadline = start + 45
reason = 'process-exit-before-adhesive-result'
failure_time = None
adhesive_base = None
adhesive_scope = None
adhesive_return = None
exception_lines = []
log_bytes = 0
pending = b''
client_marker = None
maps_captured = False
proc = None
selector = selectors.DefaultSelector()

def stop():
    if proc and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=2)
        except ProcessLookupError:
            pass

def snapshot_host_maps():
    """Read mapping metadata only; do not attach, read memory, or change target."""
    saved = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            env = (entry/'environ').read_bytes().split(b'\0')
            if ('WINEPREFIX='+str(prefix)).encode() not in env:
                continue
            cmd = (entry/'cmdline').read_bytes().split(b'\0')
            if not any(arg.lower().endswith((b'/fivem.exe', b'\\fivem.exe')) and b'fullhost' in arg.lower() for arg in cmd):
                continue
            maps = (entry/'maps').read_bytes()
            if b'fullhost/FiveM.exe' not in maps or b'ntdll.dll' not in maps:
                continue  # Wrapper argv is not evidence of the mapped host image.
            (run/('host-linux-'+entry.name+'.maps')).write_bytes(maps)
            saved.append(int(entry.name))
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
    return saved

try:
    with (run/'wine.log').open('xb') as log:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                start_new_session=True, cwd=runtime)
        selector.register(proc.stdout, selectors.EVENT_READ)
        eof = False
        while True:
            now = time.monotonic()
            for key, _ in selector.select(timeout=0.03):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    eof = True
                    continue
                log.write(chunk)
                log.flush()
                log_bytes += len(chunk)
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    s = line.decode(errors='replace')
                    scope_match = re.match(r'^([0-9A-Fa-f]+(?::[0-9A-Fa-f]+)?):(?:trace|warn|err|fixme):', s)
                    scope = scope_match[1] if scope_match else None
                    match = re.search(r'MODULE_InitDLL \(([0-9A-Fa-f]+) L"adhesive.dll",PROCESS_ATTACH,', s)
                    if not match:
                        match = re.search(r'Call PE DLL \(proc=[0-9A-Fa-f]+,module=([0-9A-Fa-f]+) L"adhesive.dll",reason=PROCESS_ATTACH,', s)
                    if match:
                        adhesive_base = match[1]
                        adhesive_scope = scope
                    if adhesive_base and scope == adhesive_scope:
                        ret = re.search(r'MODULE_InitDLL \('+adhesive_base+r',PROCESS_ATTACH,.* - RETURN (\d+)', s)
                        if not ret:
                            ret = re.search(r'Ret  PE DLL \(proc=[0-9A-Fa-f]+,module='+adhesive_base+r' L"adhesive.dll",reason=PROCESS_ATTACH,.* retval=(\d+)', s)
                        if ret:
                            adhesive_return = int(ret[1])
                            if adhesive_return:
                                reason = 'adhesive-process-attach-returned-success'
                                failure_time = failure_time or time.monotonic()
                    if 'dispatch_exception code=' in s:
                        exception_lines.append(s)
                        if opt.virtual_trace and scope == adhesive_scope and not maps_captured:
                            snapshots = snapshot_host_maps()
                            maps_captured = bool(snapshots)
                    if scope == adhesive_scope and 'Initialization of L"adhesive.dll" failed' in s:
                        reason = 'adhesive-initialization-failed'
                        failure_time = failure_time or time.monotonic()
            # Capture the normal client trace of the resulting GetLastError.
            for path in (runtime/'logs').glob('CitizenFX_log_*.log'):
                if path in existing_logs:
                    continue
                for line in path.read_text(errors='replace').splitlines():
                    if 'Adhesive failed to load under Wine (error ' in line:
                        client_marker = line
            if client_marker:
                reason = 'client-adhesive-load-failure-recorded'
                break
            if failure_time is not None and now-failure_time > 0.25:
                break
            if log_bytes > 12*1024*1024:
                reason = 'bounded-log-limit'
                break
            if now >= deadline:
                reason = 'bounded-time-limit'
                break
            if proc.poll() is not None and eof:
                break
finally:
    stop()
    selector.close()

# Terminate only services sharing this dedicated diagnostic prefix. No global
# pkill/wineserver command can affect the user's working prefix.
try:
    cleanup = subprocess.run(['flatpak', 'run', '--filesystem='+str(prefix), '--unshare=network',
                             '--nofilesystem='+str(Path.home()/'Games/FiveM-Official-Test'),
                             '--env=WINEPREFIX='+str(prefix), '--command='+str(proton/'files/bin/wineserver'),
                             'com.heroicgameslauncher.hgl', '-k'], capture_output=True, timeout=5)
    cleanup_code = cleanup.returncode
    (run/'cleanup.txt').write_bytes(cleanup.stdout+cleanup.stderr)
except subprocess.TimeoutExpired as error:
    cleanup_code = 'timeout'
    (run/'cleanup.txt').write_bytes((error.stdout or b'')+(error.stderr or b'')+b'\nScoped cleanup timeout\n')
# Preserve diagnostics already written into the pipe when the stopping marker
# arrived; an observer must not discard the tail while terminating the target.
if proc and proc.stdout:
    drain = selectors.DefaultSelector()
    drain.register(proc.stdout, selectors.EVENT_READ)
    until = time.monotonic()+0.5
    with (run/'wine.log').open('ab') as log:
        while time.monotonic()<until and log_bytes<12*1024*1024:
            ready = drain.select(timeout=0.03)
            if not ready:
                continue
            chunk = os.read(proc.stdout.fileno(),65536)
            if not chunk:
                break
            log.write(chunk)
            log_bytes += len(chunk)
    drain.close()
client_logs = []
for path in (runtime/'logs').glob('CitizenFX_log_*.log'):
    if path not in existing_logs:
        (run/path.name).write_bytes(path.read_bytes())
        client_logs.append(path.name)
summary = dict(tag=opt.tag, legacy_ui=opt.legacy_ui, virtual_trace=opt.virtual_trace, relay_trace=opt.relay_trace, maps_captured=maps_captured,
               actual_host='FiveM.exe', elapsed_seconds=round(time.monotonic()-start,2),
               stop_reason=reason, host_returncode=proc.returncode if proc else None,
               log_bytes=log_bytes, network='disabled by Flatpak',
               prefix=str(prefix), runtime=str(runtime),
               adhesive_base=adhesive_base, adhesive_scope=adhesive_scope, adhesive_attach_return=adhesive_return,
               client_failure_marker=client_marker, client_logs=client_logs,
               wineserver_cleanup_returncode=cleanup_code,
               exception_headers=exception_lines,
               hashes={name:hashlib.sha256((runtime/name).read_bytes()).hexdigest()
                       for name in ['FiveM.exe','CoreRT.dll','adhesive.dll']})
(run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
