#!/usr/bin/env python3
"""Bounded Rockstar-only experiment. Logs stay private; no account launch arguments."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument('--prefix', type=Path, required=True)
p.add_argument('--wine', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--seconds', type=int, default=55)
p.add_argument('--proton-libraries', action='store_true')
p.add_argument('--proton', type=Path)
p.add_argument('--max-log-mb', type=int, default=16)
a = p.parse_args()
prefix = a.prefix.resolve()
assert prefix.is_relative_to(Path(__file__).resolve().parents[1] / 'private')
assert not (prefix / 'drive_c/users/feras/Documents').is_symlink()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True, mode=0o700)
env = os.environ.copy()
env.update(WINEPREFIX=str(prefix), WINEDEBUG='-all,err+all,warn+all,+seh,+timestamp,+pid,+tid',
           WINEDLLOVERRIDES='winemenubuilder.exe=d')
wine = str(a.wine.resolve())
if a.proton_libraries:
    lib = a.wine.resolve().parent.parent / 'lib'
    env['WINEDLLPATH'] = ':'.join(str(lib / x) for x in ['vkd3d', 'wine'])
    env['LD_LIBRARY_PATH'] = ':'.join(str(lib / x) for x in ['x86_64-linux-gnu', 'aarch64-linux-gnu', 'i386-linux-gnu']) + ':' + env.get('LD_LIBRARY_PATH', '')
launcher = prefix / 'drive_c/Program Files/Rockstar Games/Launcher/Launcher.exe'
command = [wine, 'explorer', '/desktop=RockstarDiagnostic,1280x800', str(launcher)]
if a.proton:
    compat = out / 'compatdata'
    compat.mkdir(exist_ok=True)
    if not (compat / 'pfx').exists():
        (compat / 'pfx').symlink_to(prefix, target_is_directory=True)
    client = out / 'empty-steam-client'
    client.mkdir(exist_ok=True)
    # Match Proton's prefix and library preparation without sharing a user account.
    env.update(STEAM_COMPAT_DATA_PATH=str(compat), STEAM_COMPAT_CLIENT_INSTALL_PATH=str(client),
               SteamGameId='0', SteamAppId='0', PROTONFIXES_DISABLE='1',
               XDG_CONFIG_HOME=str(out / 'config'), XDG_DATA_HOME=str(out / 'data'))
    for name in ['Documents', 'Desktop', 'Downloads', 'Pictures', 'Music', 'Videos', 'AppData/LocalLow']:
        (prefix / 'drive_c/users/steamuser' / name).mkdir(parents=True, exist_ok=True)
    command = [str(a.proton.resolve()), 'run', 'explorer', '/desktop=RockstarDiagnostic,1280x800', str(launcher)]
start = time.time()
stop_reason = 'time_limit'
with (out / 'wine.log').open('w') as log:
    proc = subprocess.Popen(command, env=env, stdout=log, stderr=log)
    while time.time() - start < a.seconds:
        time.sleep(1)
        if (out / 'wine.log').stat().st_size > a.max_log_mb * 1024 * 1024:
            stop_reason = 'log_limit'
            break
        if int(time.time()-start) in (30, 50, 80):
            try:
                from Xlib import display, X
                from PIL import Image
                d = display.Display()
                pending = [d.screen().root]
                while pending:
                    w = pending.pop()
                    if w.get_wm_name() == 'RockstarDiagnostic - Wine Desktop' and w.get_wm_class() in [('explorer.exe', 'explorer.exe'), ('steam_proton', 'steam_proton')]:
                        g = w.get_geometry()
                        raw = w.get_image(0, 0, g.width, g.height, X.ZPixmap, 0xffffffff)
                        Image.frombytes('RGB', (g.width, g.height), raw.data, 'raw', 'BGRX').save(out / f'window-{int(time.time()-start)}.png')
                        break
                    pending.extend(w.query_tree().children)
                d.close()
            except Exception as exc:
                (out / 'snapshot-error.txt').write_text(type(exc).__name__+'\n')
    # Always stop this isolated prefix only, including detached children.
    server = next(str(x) for x in [a.wine.parent / 'wineserver', Path('/usr/lib/x86_64-linux-gnu/wine/wineserver'), Path('/usr/lib/wine/wineserver'),
                                  Path('/usr/lib/wine/wineserver64')] if x.exists())
    subprocess.run([server, '-k'], env=env, stdout=log, stderr=log, timeout=15)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.terminate()
summary = {'prefix': str(prefix), 'wine': wine, 'proton': str(a.proton) if a.proton else None, 'seconds': round(time.time()-start, 1),
           'launcher_returncode': proc.poll(), 'stop_reason': stop_reason, 'public_server_attempted': False}
(out / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary))
