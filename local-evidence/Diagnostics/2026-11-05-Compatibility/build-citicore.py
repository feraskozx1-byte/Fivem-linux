#!/usr/bin/env python3
"""Plan (default) or explicitly execute an incremental CitiCore-only build.

Run with Python 3 from a VS 2022 developer prompt on a prepared Windows
checkout. Never downloads dependencies, generates solutions, cleans outputs,
copies DLLs to runtime folders, or starts a full-client build.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2] / 'Original-PR4050-Source')
parser.add_argument('--sdk', default='10.0.22621.0')
parser.add_argument('--jobs', type=int, choices=range(1, 5), default=2)
parser.add_argument('--execute', action='store_true')
parser.add_argument('--restore', action='store_true', help='Opt in to MSBuild package restore; may require network')
args = parser.parse_args()
source = args.source.resolve()
solution = source / 'code/build/five/CitizenMP.sln'
msbuild = shutil.which('MSBuild.exe') or shutil.which('msbuild')
blockers = []
if os.name != 'nt':
    blockers.append('Requires the Windows MSVC/SDK build environment; clang-cl alone is insufficient.')
if not msbuild:
    blockers.append('MSBuild unavailable in PATH. Use a VS 2022 C++ developer prompt.')
if not solution.is_file():
    blockers.append('Generated solution missing: code/build/five/CitizenMP.sln')
else:
    if '"CitiCore"' not in solution.read_text(errors='replace'):
        blockers.append('Generated solution does not contain the CitiCore target.')

requirements = [
    'vendor/minhook/include/MinHook.h',
    'vendor/udis86/udis86.h', 'vendor/udis86/libudis86/itab.c',
    'vendor/tbb/include/tbb/tbb.h',
    'vendor/boost-submodules/boost-program-options/include/boost/program_options.hpp',
    'vendor/boost-submodules/boost-locale/include/boost/locale.hpp',
    'vendor/fmtlib/include/fmt/format.h', 'vendor/utfcpp/source/utf8.h',
]
missing = [name for name in requirements if not (source / name).is_file()]
if missing:
    blockers.append('Missing direct dependencies/generated files: ' + ', '.join(missing))
if os.name == 'nt':
    sdk_root = Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)')) / 'Windows Kits/10'
    for path in [sdk_root / 'Include' / args.sdk / 'um/Windows.h',
                 sdk_root / 'Lib' / args.sdk / 'um/x64/kernel32.lib',
                 sdk_root / 'Lib' / args.sdk / 'ucrt/x64/ucrt.lib']:
        if not path.is_file():
            blockers.append('Missing selected Windows SDK file: ' + str(path))

command = [msbuild or 'MSBuild.exe', str(solution), '/t:CitiCore',
           '/p:Configuration=Release', '/p:PreferredToolArchitecture=x64',
           '/p:WindowsTargetPlatformVersion=' + args.sdk, '/m:' + str(args.jobs),
           '/nr:false', '/v:minimal']
if args.restore:
    command += ['/restore', '/p:RestorePackagesConfig=true']
plan = {'target': 'CitiCore', 'command': command, 'blockers': blockers,
        'expected_output': str(source / 'code/bin/five/release/CoreRT.dll'),
        'reuse': 'Existing MSBuild objects and project dependencies; no clean/rebuild.',
        'deployment': 'None. Does not replace Run-Test or Run-Adhesive-Test files.',
        'preflight_scope': 'Direct prerequisites only; compiler validates remaining transitive headers/libraries.'}
print(json.dumps(plan, ensure_ascii=False, indent=2))
if args.execute:
    if blockers:
        sys.exit(2)
    # Avoid inheriting a shell's unrelated platform setting; solution chooses
    # its generated mapping, while CitiCore itself targets x64.
    environment = {key: value for key, value in os.environ.items() if key.lower() != 'platform'}
    sys.exit(subprocess.run(command, cwd=source, env=environment).returncode)
