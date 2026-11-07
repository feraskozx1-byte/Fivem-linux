#!/usr/bin/env python3
"""Prepare a small, isolated full-launcher layout. Never runs FiveM.

Original runtime binaries must be exposed read-only by the separate runner.
Only the copied INI gains the existing DisableCrashUpload option. Large game
cache files are symlinked and are never copied or hashed by this preparation.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

root = Path(__file__).resolve().parent
project = root.parents[1]
source = project / 'Run-CoreRT-Test'
adhesive = project / 'Run-Adhesive-Test/adhesive.dll'
source_code = project / 'Original-PR4050-Source'
runtime = root / 'private/fullhost'
expected_core = 'cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64'
expected_adhesive = '3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b'
matching_pdb = project / 'Diagnostics/2026-11-05-Compatibility/ci-citicore/downloaded-build/citicore-x64-42019993897/CoreRT.pdb'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

assert sha(source / 'CoreRT.dll') == expected_core
assert sha(adhesive) == expected_adhesive
assert not runtime.exists(), 'Refuse to replace a prior full-host layout.'
assert shutil.disk_usage(root).free > 16 * 1024 * 1024

# Inspect only the open-source CoreRT function, using the matching local PDB.
early_source = source_code / 'code/client/citicore/EarlyMode.Win32.cpp'
assert 'WineCompat_InstallHooks' not in early_source.read_text()
hits = subprocess.run(['rg', '-n', 'WineCompat_InstallHooks',
                       str(source_code / 'code/client'), '--glob', '*.{cpp,h}'],
                      capture_output=True, text=True, check=True).stdout
assert len(hits.splitlines()) == 1 and 'void WineCompat_InstallHooks()' in hits
exports = subprocess.check_output(['llvm-readobj', '--coff-exports', str(source/'CoreRT.dll')], text=True)
match = re.search(r'Name: EarlyMode_Init\s+RVA: (0x[0-9A-Fa-f]+)', exports)
assert match and int(match.group(1), 16) == 0x1fca0
# Matching PDB public-symbol addresses: section .text RVA1000 + offsets.
publics = subprocess.check_output(['llvm-pdbutil', 'dump', '-publics', str(matching_pdb)], text=True)
early = re.search(r'`EarlyMode_Init`\s+flags = function, addr = 0001:(\d+)', publics)
assert early and int(early.group(1)) + 0x1000 == 0x1fca0
assert 'WineCompat_InstallHooks' not in publics
pdb_summary = subprocess.check_output(['llvm-pdbutil', 'dump', '-summary', str(matching_pdb)], text=True)
old_summary = subprocess.check_output(['llvm-pdbutil', 'dump', '-summary', str(source/'dbg/CoreRT.pdb')], text=True)
debug = subprocess.check_output(['llvm-readobj', '--coff-debug-directory', str(source/'CoreRT.dll')], text=True)
expected_guid = '{D93B51AE-64C4-4ABA-8422-9C9CA823303A}'
assert expected_guid in debug and expected_guid in pdb_summary
assert expected_guid not in old_summary
disasm = subprocess.check_output(['llvm-objdump', '-d', '--start-address=0x18001fca0',
                                 '--stop-address=0x18001ff7b', str(source/'CoreRT.dll')], text=True)
assert '<EarlyMode_Init>:' in disasm and 'retq' in disasm
assert 'WineCompat_InstallHooks' not in disasm
evidence = ('CoreRT SHA256: ' + expected_core + '\n'
            'EarlyMode RVA: 0x1FCA0; bounded function region through RVA0x1FF7A.\n'
            'Matching downloaded PDB GUID: ' + expected_guid + '\n'
            'WineCompat_InstallHooks has no public symbol in matching new PDB.\n'
            'Source has no caller;\n'
            'the only source occurrence is its definition, with no static initializer.\n'
            'This is bounded source/binary inspection, not a claim about all indirect calls.\n\n' +
            hits + '\n' + disasm)
(root / 'CoreRT-EarlyMode-disassembly.txt').write_text(evidence)
(root / 'CoreRT-PDB-validation.txt').write_text('DLL CodeView:\n'+debug.split('DebugEntry {')[1].split('DebugEntry {')[0]+
    '\nCorrect downloaded PDB:\n'+pdb_summary+'\nSTALE PDB retained in original Run-CoreRT-Test/dbg:\n'+old_summary)

private = root / 'private'
private.mkdir(mode=0o700, exist_ok=True)
private.chmod(0o700)
runtime.mkdir()
entries = []
copied_bytes = 0

def copy_file(src, name):
    global copied_bytes
    dest = runtime / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    copied_bytes += dest.stat().st_size
    entries.append(dict(path=name, kind='copy', source=str(src), bytes=dest.stat().st_size,
                        source_sha256=sha(src), sha256=sha(dest)))

def link(src, name, hash_file=True):
    dest = runtime / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(src, target_is_directory=src.is_dir())
    item = dict(path=name, kind='symlink', source=str(src), requires_read_only_grant=True)
    if src.is_file():
        item['target_bytes'] = src.stat().st_size
        if hash_file:
            item['target_sha256'] = sha(src)
        else:
            item['hash_omitted'] = 'Immutable game cache or non-CoreRT debug symbols; avoid unnecessary HDD scan'
    entries.append(item)

for name in ['FiveM.exe', 'CitizenFX.ini', 'components.json', 'FiveM.exe.formaldev']:
    copy_file(source / name, name)
copy_file(source / 'CitizenFX.ini', 'CitizenFX.ini.before-phase2.bak')
ini_path = runtime / 'CitizenFX.ini'
text = ini_path.read_bytes().decode('utf-8')
assert text.count('[Game]') == 1
if re.search(r'(?im)^DisableCrashUpload=', text):
    text = re.sub(r'(?im)^DisableCrashUpload=[^\r\n]*', 'DisableCrashUpload=1', text)
else:
    text = text.replace('[Game]\r\n', '[Game]\r\nDisableCrashUpload=1\r\n', 1)
assert 'DisableCrashUpload=1' in text
ini_path.write_bytes(text.encode('utf-8'))
copied_bytes += ini_path.stat().st_size - (source / 'CitizenFX.ini').stat().st_size
for entry in entries:
    if entry['path'] == 'CitizenFX.ini':
        entry['sha256'] = sha(ini_path)
        entry['bytes'] = ini_path.stat().st_size
        entry['change'] = 'Set documented existing Game.DisableCrashUpload=1 in copied INI only'

for src in sorted(source.iterdir()):
    # .bin files are the launcher-supplied subprocess images read by CfxSubProcess.h.
    if src.is_file() and src.suffix.lower() in ['.dll', '.bin']:
        link(src, src.name)
assert not (runtime / 'adhesive.dll').exists()
link(adhesive, 'adhesive.dll')
for name in ['bin', 'citizen', 'gen']:
    link(source / name, name)
(runtime / 'dbg').mkdir()
for src in sorted((source / 'dbg').iterdir()):
    if src.is_file():
        link(matching_pdb if src.name == 'CoreRT.pdb' else src, 'dbg/' + src.name,
             hash_file=src.name == 'CoreRT.pdb')
for name in ['logs', 'crashes', 'data/cache/subprocess', 'data/game-storage']:
    (runtime / name).mkdir(parents=True, exist_ok=True)
    entries.append(dict(path=name, kind='local_directory'))
game_storage = source / 'data/game-storage'
for src in sorted(game_storage.iterdir()):
    if src.is_file():
        name = 'data/game-storage/' + src.name
        if src.name == 'game_files.dat':
            copy_file(src, name)
        else:
            link(src, name, hash_file=False)
for name in ['launcher', 'ros_2090']:
    src = game_storage / name
    if src.is_dir():
        link(src, 'data/game-storage/' + name)
assert copied_bytes < 6 * 1024 * 1024, copied_bytes
manifest = dict(runtime=str(runtime), ready=True, launched=False,
                copied_bytes=copied_bytes, large_directories_copied=False,
                core_sha256=expected_core, adhesive_sha256=expected_adhesive,
                original_sources_modified=False,
                required_readonly_paths=[str(source), str(adhesive.parent),
                                         str(matching_pdb.parent),
                                         str(Path.home()/'Games/Heroic/GTAV')],
                notes=['Do not run without read-only grants for original sources.',
                       'No ROS/nui/server account profile directories copied or linked.',
                       'Launch runner must disable network and stop after Adhesive outcome.',
                       'Only copied Game.DisableCrashUpload changed; security component selection unchanged.',
                       'Normal launcher may create additional small subprocess copies after preparation.'],
                entries=entries)
(root/'fullhost-layout.json').write_text(json.dumps(manifest, indent=2)+'\n')
print(json.dumps(dict(ready=True, launched=False, runtime=str(runtime), copied_bytes=copied_bytes,
                      entry_count=len(entries), core_sha256=expected_core), indent=2))
