#!/usr/bin/env python3
"""Test production default-build selection with simulated INI reads.

Uses the real support predicate with GAME_BUILDS expanded from premake's list.
No game, account, prefix or runtime files are changed. Requires host C++17.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Original-PR4050-Source'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=SOURCE / 'code/client/shared/XBRInit.cpp')
parser.add_argument('--expect-regression', action='store_true')
args = parser.parse_args()


def function(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


selection = function(args.source.read_text(), 'int GetDefaultBuildInit()')
runtime = (SOURCE / 'code/client/shared/CrossBuildRuntime.h').read_text()
predicate = function(runtime, 'inline bool IsSupportedGameBuild(')
defaults = {
    'five': int(re.search(r'return (\d+);', function(runtime, 'inline int GetDefaultGTA5Build()')).group(1)),
    'rdr3': int(re.search(r'return (\d+);', function(runtime, 'inline int GetDefaultRDR3Build()')).group(1)),
    'ny': int(re.search(r'#elif defined\(GTA_NY\)\s+return (\d+);', runtime).group(1)),
}
lists = (SOURCE / 'code/premake5_builds.lua').read_text()
prelude = r'''
#include <string>
#include <cstdint>
#include <cstdio>
constexpr unsigned INVALID_FILE_ATTRIBUTES = ~0u;
static bool iniExists, replaceExecutable;
static int iniDefault, requestedBuild;
static int fallbackBuild;
std::wstring MakeRelativeCitPath(const wchar_t* p) { return p; }
unsigned GetFileAttributes(const wchar_t*) { return iniExists ? 0 : INVALID_FILE_ATTRIBUTES; }
unsigned GetPrivateProfileInt(const wchar_t*, const wchar_t* name, int, const wchar_t*) {
    return std::wstring(name) == L"DefaultBuild" ? iniDefault : replaceExecutable;
}
int GetRequestedGameBuildInit() { return requestedBuild; }
int GetDefaultGameBuild() { return fallbackBuild; }
'''
tests = r'''
int main() {
    struct Case { bool exists; int value; bool replace; int requested; int expected; };
    const Case cases[] = {
        {false, 3889, false, KNOWN, FALLBACK},
        {true, KNOWN, false, FALLBACK, KNOWN},
        {true, KNOWN, true, FALLBACK, KNOWN},
        {true, 3889, false, KNOWN, FALLBACK},
        {true, 3889, true, KNOWN, KNOWN},
        {true, 999999, false, KNOWN, FALLBACK},
        {true, 999999, true, KNOWN, KNOWN},
        {true, 0, false, KNOWN, FALLBACK},
        {true, 0, true, KNOWN, KNOWN},
        {true, -1, false, KNOWN, FALLBACK},
        {true, -1, true, KNOWN, KNOWN},
        {true, 2147483647, false, KNOWN, FALLBACK},
    };
    fallbackBuild = FALLBACK;
    for (unsigned i = 0; i < sizeof(cases)/sizeof(cases[0]); ++i) {
        const auto& c = cases[i];
        iniExists = c.exists; iniDefault = c.value;
        replaceExecutable = c.replace; requestedBuild = c.requested;
        if (GetDefaultBuildInit() != c.expected) {
            std::fprintf(stderr, "selection regression case %u, INI value %d\n", i, c.value);
            return 10;
        }
    }
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='fivem-build-selection-') as temporary:
    for game in ('five', 'rdr3', 'ny'):
        section = re.search(r'\b' + game + r'\s*=\s*\{([^}]+)\}', lists).group(1)
        builds = sorted(map(int, re.findall(r'game_(\d+)\s*=', section)))
        # Substitute the generated macro expansion, retaining the actual predicate.
        expanded = re.sub(r'#define EXPAND.*?#undef EXPAND',
                          '\n'.join(f'case {b}: return true;' for b in builds),
                          predicate, flags=re.S)
        path = Path(temporary)
        cpp, exe = path / 'check.cpp', path / 'check'
        cpp.write_text(prelude + f'\n#define FALLBACK {defaults[game]}\n#define KNOWN {builds[-1] if builds[-1] != defaults[game] else builds[0]}\n'
                       + expanded + '\n' + selection + tests)
        subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                        '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                        str(cpp), '-o', str(exe)], check=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True)
        if args.expect_regression:
            assert result.returncode == 10 and 'INI value 3889' in result.stderr, result.stderr
        else:
            assert result.returncode == 0, result.stderr
print('PASS: original unsupported-build regression detected for all 3 games'
      if args.expect_regression else
      'PASS: 36 default-build cases across FiveM/RedM/LibertyM; ASan/UBSan clean')
