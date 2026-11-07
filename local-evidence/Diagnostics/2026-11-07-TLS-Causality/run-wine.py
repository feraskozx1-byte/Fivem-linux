#!/usr/bin/env python3
"""Run only our own TLS host/DLL; preserve the dedicated prefix drive mapping."""
from pathlib import Path
import argparse,hashlib,json,os,signal,subprocess,sys,time
r=Path(__file__).resolve().parent;project=r.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tag',required=True);p.add_argument('--bin',required=True,type=Path);p.add_argument('--baseline',type=Path);p.add_argument('--wine-prototype',action='store_true');p.add_argument('--direct-wine',action='store_true');o=p.parse_args()
assert o.tag and all(c.isalnum() or c=='-' for c in o.tag)
bin_dir=o.bin.resolve();assert bin_dir.is_relative_to(r)
exe=bin_dir/'tls-test.exe';dll=bin_dir/'tls-fixture.dll';assert exe.is_file() and dll.is_file()
result=bin_dir/'tls-result.txt';assert not result.exists(),'Preserve prior result first'
run=r/'private'/o.tag;run.mkdir(mode=0o700)
prefix=project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix'
s=prefix/'dosdevices/s:';old_s=os.readlink(s) if s.is_symlink() else None
(run/'drive-backup.json').write_text(json.dumps({'s':old_s})+'\n')
heroic=Path.home()/'.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic'
proton=heroic/'tools/proton/Proton-CachyOS-latest';umu=heroic/'tools/runtimes/umu/umu-run'
args=['flatpak','run','--filesystem='+str(r),'--filesystem='+str(prefix),'--unshare=network',
 '--nofilesystem='+str(Path.home()/'Games/FiveM-Official-Test'),
 '--env=WINEPREFIX='+str(prefix),'--env=PROTONPATH='+str(proton),'--env=GAMEID=umu-default',
 '--env=UMU_RUNTIME_UPDATE=0','--env=PROTONFIXES_DISABLE=1','--env=PROTON_USE_PIPEWIRE=0',
 '--env=PROTON_FSR4_UPGRADE=0','--env=WINEDLLOVERRIDES=winemenubuilder.exe=d','--env=WINEDEBUG=-all',
 '--command='+str(umu),'com.heroicgameslauncher.hgl',str(exe)]
hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [exe,dll,bin_dir/'tls-control.dll']}
if o.direct_wine:args=[('--command='+str(proton/'files/bin/wine')) if x=='--command='+str(umu) else x for x in args]
if o.wine_prototype:args=[sys.executable,str(r/'mount-wine-prototype.py'),*args]
start=time.monotonic();timed_out=False;child=None
try:
 with (run/'wrapper.log').open('xb') as log:
  child=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,cwd=bin_dir,start_new_session=True)
  try:child.wait(timeout=55)
  except subprocess.TimeoutExpired:
   timed_out=True;os.killpg(child.pid,signal.SIGTERM)
   try:child.wait(timeout=2)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
finally:
 try:
  x=subprocess.run(['flatpak','run','--filesystem='+str(prefix),'--unshare=network','--env=WINEPREFIX='+str(prefix),'--command='+str(proton/'files/bin/wineserver'),'com.heroicgameslauncher.hgl','-k'],capture_output=True,timeout=5)
  (run/'cleanup.txt').write_bytes(x.stdout+x.stderr)
 except subprocess.TimeoutExpired:(run/'cleanup.txt').write_text('Scoped cleanup timeout\n')
 if s.is_symlink():s.unlink()
 if old_s is not None:s.symlink_to(old_s)
content=result.read_text(errors='replace') if result.exists() else ''
if result.exists():(run/'results.txt').write_text(content);result.unlink()
native=o.baseline.read_text(errors='replace') if o.baseline else ''
obs=[x for x in content.splitlines() if x.startswith('OBS ')]
native_obs=[x for x in native.splitlines() if x.startswith('OBS ')]
out={'tag':o.tag,'Wine_source_backed_prototype':o.wine_prototype,'transport':'UMU/Proton-CachyOS via Heroic Flatpak','returncode':child.returncode if child else None,'timed_out':timed_out,'elapsed_seconds':round(time.monotonic()-start,2),'hashes':hashes,'pass_count':content.count('PASS '),'fail_count':content.count('FAIL '),'complete':'RESULT=' in content,'success':'RESULT=PASS' in content and child.returncode==0,'network':'disabled','FiveM_or_Adhesive_loaded':False,'native_observations_match':obs==native_obs if native else None,'Wine_observations':obs,'native_observations':native_obs,'binaries_unchanged':all(hashlib.sha256((bin_dir/n).read_bytes()).hexdigest()==h for n,h in hashes.items())}
if o.direct_wine:out['transport']='direct Proton Wine via Heroic Flatpak (no UMU remount)'
def api_values(text):
 return {line.split('=',1)[0]:line.split('=',1)[1] for line in text.splitlines()
         if line.startswith(('LdrDisableThreadCalloutsForDll-static-status=',
             'DisableThreadLibraryCalls-static-return=',
             'DisableThreadLibraryCalls-control-return='))}
out['public_API_values']=api_values(content)
out['public_API_returns_match_native']=api_values(content)==api_values(native) if native else None
out['intended_prototype_behavior_observed']=(api_values(content).get('LdrDisableThreadCalloutsForDll-static-status')=='0x0000000000000000'
 and api_values(content).get('DisableThreadLibraryCalls-static-return')=='0x0000000000000001') if o.wine_prototype else None
(run/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(content);print(json.dumps(out,indent=2))
