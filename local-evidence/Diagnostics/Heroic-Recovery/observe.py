#!/usr/bin/env python3
"""Metadata-only observation of the recovered FiveM test; never reads process memory."""
import json
from pathlib import Path
import time

base = Path('/home/feras/Games/FiveM-Official-Test')
prefix = (base / 'GTA-Prefix-Work').resolve()
result = {'observed_at_unix': time.time(), 'processes': [], 'recent_logs': []}
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():
        continue
    try:
        env = dict(x.split(b'=', 1) for x in (proc / 'environ').read_bytes().split(b'\0') if b'=' in x)
        if Path(env.get(b'WINEPREFIX', b'/nonexistent').decode()).resolve() != prefix:
            continue
        maps = (proc / 'maps').read_text()
        paths = sorted(set(line[line.index('/'):] for line in maps.splitlines() if '/' in line))
        selected = [s for s in paths if any(x in s.lower() for x in ['sticky.dll', 'adhesive.dll', 'legitimacy.dll', 'winepipewire', 'winepulse', 'winealsa'])]
        executable = [s for s in paths if s.lower().endswith('.exe') and ('fivem' in s.lower() or 'rockstar' in s.lower())]
        if not executable and not selected:
            continue
        result['processes'].append({'pid': int(proc.name), 'name': (proc / 'comm').read_text().strip(),
                                    'mapped_executables': executable, 'selected_modules': selected,
                                    'audio_driver': env.get(b'WINE_AUDIO_DRIVER', b'').decode(),
                                    'pipewire_setting': env.get(b'PROTON_USE_PIPEWIRE', b'').decode()})
    except (OSError, ValueError, UnicodeError):
        continue
for directory in [base / 'Official-Client-Staging/logs', base / 'installer/FiveM.app/logs']:
    for log in sorted(directory.glob('CitizenFX_log*'), key=lambda f: f.stat().st_mtime, reverse=True)[:2]:
        if time.time() - log.stat().st_mtime > 1800:
            continue
        data = log.read_text(errors='replace')
        result['recent_logs'].append({'path': str(log), 'bytes': log.stat().st_size,
            'rockstar_signed_in': "MTL says it's signed in" in data,
            'game_initialized': 'INIT_CORE' in data and 'Done running INIT_CORE' in data,
            'server_handshake': 'handshake' in data.lower(),
            'missing_auth_ticket': 'No authentication ticket was specified' in data,
            'ros_error_506': 'ExitCode: 506' in data or 'ExitCode 506' in data})
print(json.dumps(result, indent=2))
Path(__file__).with_name('private').joinpath('latest-observation.json').write_text(json.dumps(result, indent=2)+'\n')
