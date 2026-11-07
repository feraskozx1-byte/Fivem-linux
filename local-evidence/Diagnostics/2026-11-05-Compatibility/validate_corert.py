#!/usr/bin/env python3
"""Exercise the actual HardErrorScope class with mocked Windows/MinHook APIs.

This is a host C++ regression harness, not a Windows DLL build or a Proton test.
An inaccessible mapping represents Wine's _fltused-adjacent storage. The scope
must never resolve or touch it on Wine, including during destruction.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

BASE = Path(__file__).resolve().parents[2]
source = BASE / 'Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=source)
source = parser.parse_args().source
text = source.read_text()
production = text[text.index('static NTSTATUS(NTAPI* g_origRtlRaiseException)'):text.index('Component* DllGameComponent::CreateComponent()')]
prefix = r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <sys/mman.h>
#include <unistd.h>
#include <iostream>
#define NTAPI
#define _In_
using NTSTATUS = int;
using BOOL = int;
using ULONG = unsigned long;
using WORD = uint16_t;
struct EXCEPTION_RECORD { unsigned ExceptionCode; uintptr_t ExceptionInformation[2]; };
using PEXCEPTION_RECORD = EXCEPTION_RECORD*;
constexpr unsigned DBG_PRINTEXCEPTION_C = 0x40010006;
constexpr int STATUS_SUCCESS = 0;
struct DisableToolHelpScope { ~DisableToolHelpScope() {} };
struct FakePeb { unsigned char padding[0x120]; WORD build; } peb;
struct FakeTeb { void* ProcessEnvironmentBlock = &peb; } teb;
static bool wine;
static int lookups;
static char* fltUsed;
bool CfxIsWine() { return wine; }
FakeTeb* NtCurrentTeb() { return &teb; }
void* GetModuleHandle(const wchar_t*) { return &peb; }
void* GetProcAddress(void*, const char* name) {
    if (!strcmp(name, "_fltused")) { ++lookups; return fltUsed; }
    return nullptr;
}
void MH_Initialize() {}
template<class T> void MH_CreateHook(void*, T, void**) {}
void MH_EnableHook(void*) {}
void MH_DisableHook(void*) {}
void MH_RemoveHook(void*) {}
std::wstring ToWide(const std::string& s) { return std::wstring(s.begin(), s.end()); }
'''
suffix = r'''
int main() {
    const auto pageSize = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    auto inaccessible = mmap(nullptr, pageSize, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(inaccessible != MAP_FAILED);
    unsigned cases = 0;
    for (WORD build : {18361, 18362, 19045, 19627, 19628, 22000}) {
        peb.build = build;
        wine = true;
        lookups = 0;
        fltUsed = static_cast<char*>(inaccessible) + 16;
        { HardErrorScope scope; }
        assert(lookups == 0);
        ++cases;
        for (int initial : {0, 0x40}) {
            wine = false;
            lookups = 0;
            alignas(int) char storage[32]{};
            *reinterpret_cast<int*>(storage) = initial;
            fltUsed = storage + 16;
            const bool active = build >= 18362 && build < 19628;
            {
                HardErrorScope scope;
                assert(*reinterpret_cast<int*>(storage) == (active ? initial | 2 : initial));
                assert(lookups == (active ? 1 : 0));
            }
            assert(*reinterpret_cast<int*>(storage) == initial);
            assert(lookups == (active ? 2 : 0));
            ++cases;
        }
    }
    assert(munmap(inaccessible, pageSize) == 0);
    std::cout << "PASS: " << cases << " HardErrorScope cases; Wine inaccessible storage untouched, native flags restored\n";
}
'''
with tempfile.TemporaryDirectory(prefix='fivem-corert-check-') as directory:
    cpp = Path(directory) / 'check.cpp'
    binary = Path(directory) / 'check'
    cpp.write_text(prefix + production + suffix)
    subprocess.run(['clang++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
