#!/usr/bin/env python3
"""Reject a solution containing anything outside the native CitiCore graph."""
import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser()
p.add_argument('solution', type=Path)
p.add_argument('--manifest', type=Path, required=True)
p.add_argument('--allow-uninitialized-deps', action='store_true')
args = p.parse_args()
manifest = json.loads(args.manifest.read_text())
expected = set(manifest['projects'])
projects = re.findall(r'Project\("[^"\n]+"\) = "([^"]+)", "([^"]+\.vcxproj)"', args.solution.read_text())
assert {name for name, _ in projects} == expected, projects
assert len(projects) == len(expected)
ns = {'m': 'http://schemas.microsoft.com/developer/msbuild/2003'}
result = {}
for name, relative in projects:
    path = args.solution.parent / relative.replace('\\', '/')
    tree = ET.parse(path)
    configurations = [v.attrib['Include'] for v in tree.findall('.//m:ProjectConfiguration', ns)]
    assert 'Release|x64' in configurations and all(v.endswith('|x64') for v in configurations), configurations
    assert not tree.findall('.//m:PackageReference', ns)
    references = [Path(v.attrib['Include'].replace('\\', '/')).stem for v in tree.findall('.//m:ProjectReference', ns)]
    assert set(references) <= expected
    units = [v.attrib['Include'] for v in tree.findall('.//m:ClCompile[@Include]', ns)]
    missing = [v for v in units if not (path.parent / v.replace('\\', '/')).exists()]
    if not args.allow_uninitialized_deps:
        assert units and not missing, (name, missing)
    result[name] = {'references': references, 'translation_units': len(units), 'missing_units': len(missing)}
assert result['CitiCore']['translation_units'] >= 30
assert result['Shared']['translation_units'] >= 10
print(json.dumps({'graph_verified': True, 'mode': 'topology-only' if args.allow_uninitialized_deps else 'ready-for-compile',
                  'projects': result}, indent=2))
