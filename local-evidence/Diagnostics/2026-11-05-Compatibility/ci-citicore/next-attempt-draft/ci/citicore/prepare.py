#!/usr/bin/env python3
"""Prepare isolated CitiCore generation using the pinned project's build rules.

Creates three new Lua entry files; never replaces production C++ or original
Premake files. Required generated headers remain normal IDL custom-build jobs.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
args = parser.parse_args()
root = args.source.resolve()
code = root / 'code'
base = (code / 'premake5.lua').read_text()
prefix, remaining = base.split('\t-- TARGET: launcher', 1)
assert 'include \'client/citicore\'' in remaining
assert prefix.count("dofile('components/config.lua')") == 1
assert prefix.count("dofile('vendor/config.lua')") == 1
prefix = prefix.replace("dofile('components/config.lua')", '-- Native core build: no game components.')
prefix = prefix.replace("load_privates('privates_config.lua')", '-- No private components in this native-core build.')
prefix = prefix.replace("dofile('vendor/config.lua')", "dofile('vendor/config-citicore.lua')")
prefix = prefix.replace("startproject 'CitiLaunch'", "startproject 'CitiCore'")
tail = '''
    -- Only the native core and its existing static-library dependencies.
    include 'client/citicore'
    include 'client/shared/premake5-citicore.lua'
    group 'vendor'
    do_vendor()
end, function(e)
    print(e)
    print(debug.traceback())
    os.exit(1)
end)
'''
shared = (code / 'client/shared/premake5.lua').read_text()
assert shared.count('do_shared(true)') == 1
assert shared.count("dependson { 'CfxPrebuild' }") == 1
# The full-client utility generates C#/JS native bindings and downloads native
# metadata. Neither is consumed by these projects. udis86 generation and IDL
# Python packages are prepared explicitly by the scoped workflow instead.
shared = shared.replace('do_shared(true)', '-- SharedLibc is not linked by CitiCore.')
shared = shared.replace("dependson { 'CfxPrebuild' }", '-- Target-specific preparation runs before generation.')
vendors = ['boost_program_options', 'tbb', 'minhook', 'udis86', 'boost_locale', 'fmtlib', 'utfcpp']
generated = {
    code / 'premake5-citicore.lua': prefix + tail,
    code / 'vendor/config-citicore.lua': ''.join("vendor_component '" + v + "'\n" for v in vendors),
    code / 'client/shared/premake5-citicore.lua': shared,
}
for path, content in generated.items():
    if path.exists() and path.read_text() != content:
        raise SystemExit('Refusing to overwrite a different generated file: ' + str(path))
    path.write_text(content)

tracked = subprocess.check_output(['git', 'ls-tree', '-r', 'HEAD', 'vendor/boost-submodules'], cwd=root, text=True)
available = {line.split('\t', 1)[1] for line in tracked.splitlines()}
boost = sorted(set(re.findall(r'\.\./(vendor/boost-submodules/[^/]+)/include', prefix)))
assert boost and all(path in available for path in boost)
dependencies = ['vendor/minhook', 'vendor/udis86', 'vendor/tbb', 'vendor/fmtlib',
                'vendor/utfcpp', 'vendor/jitasm', 'vendor/rapidjson', 'vendor/nljson'] + boost
manifest = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
            'submodules': dependencies,
            'projects': ['CitiCore', 'Shared', *vendors],
            'excluded': ['CEF', 'Node', 'GTA data', 'C#', 'launcher', 'game components', 'full-client prebuild']}
(code / 'citicore-build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Prepared {len(manifest["projects"])} native projects and {len(dependencies)} selected submodules; no downloads.')
