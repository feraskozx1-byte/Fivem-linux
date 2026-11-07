#!/usr/bin/env python3
"""Run extracted EarlyMode_Init with fake components, without security DLLs."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=ROOT / 'Original-PR4050-Source/code/client/citicore/EarlyMode.Win32.cpp')
parser.add_argument('--expect-regression', action='store_true')
args = parser.parse_args()
text = args.source.read_text()
body = text[text.index('extern "C" DLL_EXPORT void EarlyMode_Init()'):text.rindex('#endif')]
prelude = r'''
#include <string>
#include <vector>
#include <cstdio>
#define DLL_EXPORT
static unsigned hiddenHooks;
static std::vector<std::string> events;
void WineCompat_InstallHooks() { ++hiddenHooks; }
struct Component { virtual ~Component() {} };
struct LifeCycleComponent : Component {
    std::string name;
    void PreInitGame() { events.push_back("preinit:" + name); }
};
template<class T> struct fwRefContainer {
    T* value;
    fwRefContainer(T* v) : value(v) {}
    T* operator->() { return value; }
    T* GetRef() { return value; }
};
template<class T> T dynamic_component_cast(Component* v) { return dynamic_cast<T>(v); }
struct ComponentData {
    LifeCycleComponent component;
    Component* CreateInstance(const char*) {
        events.push_back("create:" + component.name); return &component;
    }
};
struct ComponentLoader {
    ComponentData values[2];
    unsigned next = 0;
    static ComponentLoader* GetInstance() { static ComponentLoader v; return &v; }
    void Initialize() { events.push_back("initialize"); }
    ComponentData* LoadComponent(const char* name) {
        events.push_back(std::string("load:") + name);
        auto* p = &values[next++]; p->component.name = name; return p;
    }
};
int fake_putenv(const char* value) { events.push_back(value); return 0; }
#define putenv fake_putenv
struct DisableToolHelpScope { ~DisableToolHelpScope() {} };
'''
tests = r'''
int main() {
    EarlyMode_Init();
    if (hiddenHooks != 0) { std::fputs("identity hook still activated\n", stderr); return 10; }
    const std::vector<std::string> wanted = {
        "CitizenFX_ToolMode=1", "initialize", "CitizenFX_ToolMode=",
        "load:legitimacy", "create:legitimacy", "load:adhesive", "create:adhesive",
        "preinit:legitimacy", "preinit:adhesive"
    };
    if (events != wanted) return 11;
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='fivem-transparent-start-') as temporary:
    p = Path(temporary)
    (p / 'test.cpp').write_text(prelude + body + tests)
    subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                    str(p / 'test.cpp'), '-o', str(p / 'test')], check=True)
    result = subprocess.run([str(p / 'test')], capture_output=True, text=True)
    if args.expect_regression:
        assert result.returncode == 10 and 'identity hook' in result.stderr, result.stderr
    else:
        assert result.returncode == 0, result.stderr
print('PASS: old startup identity-hook activation detected' if args.expect_regression else
      'PASS: no identity-hook activation; component creation/preinit order preserved; ASan/UBSan clean')
