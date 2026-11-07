#!/usr/bin/env python3
"""Probe public loaded PE export tables under the same Proton prefix."""
from pathlib import Path
import argparse,json,subprocess,time,os,signal,hashlib
root=Path(__file__).resolve().parent; project=root.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tag',required=True);p.add_argument('--direct-wine',action='store_true');o=p.parse_args()
assert o.tag and all(c.isalnum() or c=='-' for c in o.tag)
private=root/'private';private.mkdir(mode=0o700,exist_ok=True);private.chmod(0o700)
run=private/o.tag;run.mkdir(mode=0o700)
prefix=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
result=prefix/'drive_c/rca-export-probe-result.txt';assert not result.exists(),'Preserve previous results before rerunning'
assert not (prefix/'drive_c/compat-fix-fixture-20261105.bin').exists(),'Previous fixture retained: inspect before rerun'
heroic=Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
proton=heroic/'tools/proton/Proton-CachyOS-latest';umu=heroic/'tools/runtimes/umu/umu-run'
args=['flatpak','run','--filesystem='+str(root),'--filesystem='+str(prefix),'--unshare=network',
 '--nofilesystem='+str(Path.home()/'Games/FiveM-Official-Test'),
 '--env=WINEPREFIX='+str(prefix),'--env=PROTONPATH='+str(proton),'--env=GAMEID=umu-default',
 '--env=UMU_RUNTIME_UPDATE=0','--env=PROTONFIXES_DISABLE=1','--env=PROTON_USE_PIPEWIRE=0',
 '--env=PROTON_FSR4_UPGRADE=0','--env=WINEDLLOVERRIDES=winemenubuilder.exe=d','--env=WINEDEBUG=-all',
 '--command='+str(umu),'com.heroicgameslauncher.hgl',str(root/'export-probe.exe')]
if o.direct_wine:
 args[args.index('--command='+str(umu))]='--command='+str(proton/'files/bin/wine')
start=time.monotonic();timeout=False
with (run/'wrapper.log').open('xb') as log:
 child=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=child.wait(timeout=55)
 except subprocess.TimeoutExpired:
  timeout=True;os.killpg(child.pid,signal.SIGTERM)
  try:code=child.wait(timeout=2)
  except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);code=child.wait()
content=result.read_bytes() if result.exists() else b''
if content:(run/'results.txt').write_bytes(content);result.unlink()
summary=dict(tag=o.tag,transport='direct Wine in Heroic Flatpak' if o.direct_wine else 'UMU/Proton',returncode=code,timed_out=timeout,elapsed_seconds=round(time.monotonic()-start,2),
 exe_sha256=hashlib.sha256((root/'export-probe.exe').read_bytes()).hexdigest(),
 network='Flatpak unshare network',five_m_libraries_loaded=False,
 pass_count=content.count(b'PASS '),fail_count=content.count(b'FAIL '),
 complete=b'RESULT=' in content,success=b'RESULT=PASS' in content and code==0)
(run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(content.decode(errors='replace'));print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['success'] else 1)
