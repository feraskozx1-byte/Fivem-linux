#!/usr/bin/env python3
"""Visible hardware-breakpoint trace; fixture validation precedes real host use."""
from pathlib import Path
import argparse, hashlib, json, os, selectors, signal, subprocess, sys, time

root = Path(__file__).resolve().parent
project = root.parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tag', required=True)
p.add_argument('--fixture', action='store_true')
p.add_argument('--direct-wine', action='store_true')
opt = p.parse_args()
assert opt.tag and all(c.isalnum() or c == '-' for c in opt.tag)
run = root/'private'/opt.tag
run.mkdir(parents=True, mode=0o700)
prefix = project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
runtime = project/'Diagnostics/2026-11-05-Adhesive-Phase2/private/fullhost'
heroic = Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
proton = heroic/'tools/proton/Proton-CachyOS-latest'
umu = heroic/'tools/runtimes/umu/umu-run'
names = ['export-resolver-observer.txt','export-fixture.txt']
assert all(not (prefix/'drive_c'/name).exists() for name in names), 'Archive previous C: snapshots first'
assert (prefix/'dosdevices/z:').resolve() == Path('/')
observer = root/('resolver-observer-fixture.exe' if opt.fixture else 'resolver-observer-host.exe')
assert observer.is_file(), 'Build must succeed before starting Proton'
if not opt.fixture:
    validation=json.loads((root/'observer-validation.json').read_text())
    assert validation['passed'] and validation['source_sha256']==hashlib.sha256((root/'resolver-observer.c').read_bytes()).hexdigest(), 'Validate this observer version on the independent fixture first'
    assert validation['host_observer_sha256']==hashlib.sha256(observer.read_bytes()).hexdigest(), 'Fixture validation must match this build'
    (run/'observer-build-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
drive_s=prefix/'dosdevices/s:'
drive_s_before=os.readlink(drive_s) if drive_s.is_symlink() else None
(run/'drive-mapping-backup.json').write_text(json.dumps({'s':drive_s_before})+'\n')
assert hashlib.sha256((runtime/'adhesive.dll').read_bytes()).hexdigest() == '3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b'
before_logs = set((runtime/'logs').glob('*'))
hashes = {name:hashlib.sha256((runtime/name).read_bytes()).hexdigest() for name in ['FiveM.exe','CoreRT.dll','adhesive.dll']}
args = ['flatpak','run','--filesystem='+str(root),'--filesystem='+str(prefix),'--filesystem='+str(runtime),
        '--nofilesystem='+str(Path.home()/'Games/FiveM-Official-Test'),
        '--filesystem='+str(project/'Run-CoreRT-Test')+':ro',
        '--filesystem='+str(project/'Run-Adhesive-Test')+':ro',
        '--filesystem='+str(project/'Diagnostics/2026-11-05-Compatibility/ci-citicore/downloaded-build/citicore-x64-42019993897')+':ro',
        '--filesystem='+str(Path.home()/'Games/Heroic/GTAV')+':ro', '--unshare=network',
        '--env=WINEPREFIX='+str(prefix), '--env=PROTONPATH='+str(proton),
        '--env=GAMEID=umu-default','--env=UMU_RUNTIME_UPDATE=0','--env=PROTONFIXES_DISABLE=1',
        '--env=PROTON_USE_PIPEWIRE=0','--env=PROTON_FSR4_UPGRADE=0',
        '--env=WINEDLLOVERRIDES=winemenubuilder.exe=d','--env=CitizenFX_NoTenUI=1',
        '--env=WINEDEBUG=-all', '--command='+str(umu),
        'com.heroicgameslauncher.hgl', str(observer)]
if opt.fixture:
    args = [x for x in args if not x.startswith('--filesystem=') or x in ['--filesystem='+str(root),'--filesystem='+str(prefix)]]
if opt.direct_wine:args=[('--command='+str(proton/'files/bin/wine')) if x=='--command='+str(umu) else x for x in args]
start = time.monotonic()
proc = None
reason = 'process-exit'
size = 0
try:
    proc = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,cwd=root if opt.fixture else runtime)
    select = selectors.DefaultSelector()
    select.register(proc.stdout,selectors.EVENT_READ)
    with (run/'wine.log').open('xb') as output:
        eof = False
        while not (eof and proc.poll() is not None):
            for key,_ in select.select(0.05):
                data = os.read(key.fd,65536)
                if not data:
                    select.unregister(key.fileobj)
                    eof = True
                    continue
                output.write(data)
                size += len(data)
            if time.monotonic()-start>55:
                reason = 'time-bound'
                break
            # The observer may finish while a child launcher keeps wine alive.
            # Its flushed final marker precedes ExitProcess; stop only after the
            # complete record, then perform cleanup scoped to this test prefix.
            snapshot=prefix/'drive_c/export-resolver-observer.txt'
            if not opt.fixture and snapshot.is_file() and snapshot.stat().st_size<1024*1024:
                with snapshot.open('rb') as sf:
                    sf.seek(max(0,snapshot.stat().st_size-256))
                    if b'OBSERVER_COMPLETE' in sf.read():
                        reason='observer-complete'
                        break
            if size>12*1024*1024:
                reason = 'log-bound'
                break
    select.close()
finally:
    if proc and proc.poll() is None:
        try:
            os.killpg(proc.pid,signal.SIGTERM)
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL)
            proc.wait(timeout=2)
    try:
        result = subprocess.run(['flatpak','run','--filesystem='+str(prefix),'--unshare=network',
            '--env=WINEPREFIX='+str(prefix),'--command='+str(proton/'files/bin/wineserver'),
            'com.heroicgameslauncher.hgl','-k'],capture_output=True,timeout=5)
        (run/'cleanup.txt').write_bytes(result.stdout+result.stderr)
    except subprocess.TimeoutExpired:
        (run/'cleanup.txt').write_text('Scoped cleanup timeout\n')
    if drive_s.is_symlink():
        drive_s.unlink()
    if drive_s_before is not None:
        drive_s.symlink_to(drive_s_before)
    for name in names:
        src = prefix/'drive_c'/name
        if src.exists():
            (run/name).write_bytes(src.read_bytes())
            src.unlink()
    for path in (runtime/'logs').glob('*'):
        if path not in before_logs and path.is_file():
            (run/path.name).write_bytes(path.read_bytes())
    after = {name:hashlib.sha256((runtime/name).read_bytes()).hexdigest() for name in hashes}
    summary = dict(tag=opt.tag,fixture=opt.fixture,elapsed_seconds=round(time.monotonic()-start,2),stop_reason=reason,
        transport='direct Proton Wine via Flatpak' if opt.direct_wine else 'UMU/Proton via Flatpak',
        runner_returncode=proc.returncode if proc else None,log_bytes=size,network='disabled',
        debugger_visible=True,hardware_debug_registers=True,resume_flag_for_debugger_only=True,process_memory_writes=False,debugger_API_return_overrides=False,
        hashes=hashes,files_unchanged=hashes==after,
        samples={name:(run/name).stat().st_size for name in names if (run/name).exists()})
    (run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
