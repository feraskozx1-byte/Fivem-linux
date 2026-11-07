#!/usr/bin/env bash
# Launch the existing Heroic test entry after its backed-up targetExe correction.
set -euo pipefail
python3 - <<'PY'
import json
from pathlib import Path
p = Path('/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/GamesConfig/wC6nr6dqw6GVLd8H6ysDhV.json')
assert json.loads(p.read_text())['wC6nr6dqw6GVLd8H6ysDhV'].get('targetExe') == '/home/feras/Games/FiveM-Official-Test/Official-Portable/FiveM.exe', 'Baseline launcher disabled: the temporary Heroic target has been restored.'
PY
exec flatpak run \
  --env=CitizenFX_NoTenUI=1 \
  --env=PROTON_USE_PIPEWIRE=0 \
  --env=WINEDEBUG=-all,err+all \
  --command=sh com.heroicgameslauncher.hgl -c '
    export XDG_CONFIG_HOME=/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2
    exec /app/bin/heroic-run "$@"
  ' sh --no-gui \
  'heroic://launch?appName=wC6nr6dqw6GVLd8H6ysDhV&runner=sideload&gui=false'
