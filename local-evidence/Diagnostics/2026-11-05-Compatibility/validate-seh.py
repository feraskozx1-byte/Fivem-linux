#!/usr/bin/env python3
"""Compile actual SEH override/setup functions against mock Win32/MinHook APIs.

Checks control flow, function table ABI semantics and module boundaries only.
This is NOT a Windows build or a Wine SEH/unwinding integration test.
Requires Python 3 and a host C++17 compiler; creates temporary files only.
"""
from pathlib import Path
import os
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[2] / 'Original-PR4050-Source' /
          'code/client/citicore/SEHTableHandler.Win32.cpp').read_text()
start = source.index('struct FUNCTION_TABLE_DATA')
end = source.index('\n#else\nvoid DLL_EXPORT CoreRT_SetupSEHHandler', start)
production = source[start:end].replace('#include <winternl.h>', '')
# Existing native Windows code relies on MSVC's function-pointer-to-void*
# extension. Add explicit casts in the host test only (no behavior change).
for name in ('RtlpxLookupFunctionTableOverride', 'RtlpxLookupFunctionTableOverrideDownLevel'):
    production = production.replace('= ' + name + ';', '= reinterpret_cast<void*>(' + name + ');')
prelude = r'''
#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <stdexcept>
#include <type_traits>
using DWORD = uint32_t;
using ULONG = uint32_t;
using DWORD64 = uint64_t;
using PDWORD64 = DWORD64*;
using PULONG = ULONG*;
using NTSTATUS = int32_t;
using HANDLE = void*;
using PVOID = void*;
using HMODULE = void*;
using BOOL = int;
using INT = int;
using WORD = uint16_t;
using SIZE_T = size_t;
using PSIZE_T = SIZE_T*;
struct RUNTIME_FUNCTION { DWORD BeginAddress, EndAddress, UnwindData; };
using PRUNTIME_FUNCTION = RUNTIME_FUNCTION*;
#define NTAPI
#define DLL_EXPORT
#define IMAGE_DIRECTORY_ENTRY_EXCEPTION 3
#define MH_ALL_HOOKS nullptr
constexpr int MH_OK = 0;
constexpr int UD_Ijmp = 1;
static bool wine = true, win81 = false, win8 = true, exportPresent = true;
static int createStatus, enableStatus, creates, enables, scans, versionChecks, queries;
static void* lastTarget;
static void* lastEnabled;
static void* lastReplacement;
static void* forwardedAddress;
static PDWORD64 forwardedBase;
static PULONG forwardedLength;
static HMODULE directoryModule;
static BOOL directoryMapped;
static WORD directoryIndex;
static ULONG* directoryLength;
static int directoryCalls;
static PVOID originalDirectory(HMODULE module, BOOL mapped, WORD index, ULONG* length)
{
    ++directoryCalls;
    directoryModule = module; directoryMapped = mapped; directoryIndex = index; directoryLength = length;
    *length = 55;
    return reinterpret_cast<void*>(0xDDD);
}
static void* const lookupAddress = reinterpret_cast<void*>(0x5000);
static void* originalLookup(void* address, PDWORD64 base, PULONG len)
{
    forwardedAddress = address; forwardedBase = base; forwardedLength = len;
    *base = 0xABC; *len = 9;
    return reinterpret_cast<void*>(0xEEE);
}
static bool CfxIsWine() { return wine; }
static bool IsWindows8Point1OrGreater() { ++versionChecks; return win81; }
static bool IsWindows8OrGreater() { ++versionChecks; return win8; }
static HANDLE GetCurrentProcess() { return nullptr; }
static HMODULE GetModuleHandle(const wchar_t* name)
{
    if (name && !std::wcscmp(name, L"xtajit64.dll")) return nullptr;
    return reinterpret_cast<void*>(0x4000);
}
static NTSTATUS queryMemory(HANDLE, PVOID, int, PVOID out, SIZE_T, PSIZE_T)
{
    ++queries; std::memset(out, 0, 24); return -1;
}
static void* GetProcAddress(HMODULE, const char* name)
{
    if (!std::strcmp(name, "RtlImageDirectoryEntryToData")) return exportPresent ? lookupAddress : nullptr;
    if (!std::strcmp(name, "NtQueryVirtualMemory")) return reinterpret_cast<void*>(queryMemory);
    return reinterpret_cast<void*>(0x7000);
}
static void* FindCallFromAddress(void*, int = 0, bool = false)
{
    ++scans; return reinterpret_cast<void*>(0x6000);
}
struct DisableToolHelpScope {};
[[noreturn]] static void FatalError(const char* message, ...)
{
    throw std::runtime_error(message);
}
static void trace(const char*, ...) {}
template<class F>
static int MH_CreateHook(void* target, F replacement, void** original)
{
    ++creates; lastTarget = target; lastReplacement = reinterpret_cast<void*>(replacement);
    if (createStatus != MH_OK) return createStatus;
    if constexpr (std::is_same_v<F, PVOID(*)(HMODULE, BOOL, WORD, ULONG*)>)
        *original = reinterpret_cast<void*>(originalDirectory);
    else
        *original = reinterpret_cast<void*>(originalLookup);
    return MH_OK;
}
template<class F>
static int MH_CreateHookApi(const wchar_t*, const char*, F replacement, void** original)
{
    return MH_CreateHook(reinterpret_cast<void*>(0x7000), replacement, original);
}
static int MH_EnableHook(void* target)
{
    ++enables; lastEnabled = target; return enableStatus;
}
'''
tests = r'''
static void reset()
{
    wine = true; win81 = false; win8 = true; exportPresent = true;
    createStatus = enableStatus = creates = enables = scans = versionChecks = queries = 0;
    lastTarget = lastEnabled = lastReplacement = nullptr;
    forwardedAddress = nullptr; forwardedBase = nullptr; forwardedLength = nullptr;
    directoryModule = nullptr; directoryMapped = 0; directoryIndex = 0; directoryLength = nullptr; directoryCalls = 0;
}
int main()
{
    RUNTIME_FUNCTION functions[3]{};
    reset();
    CoreRT_SetupSEHHandler(reinterpret_cast<void*>(0x1000), reinterpret_cast<void*>(0x2000), functions, 3);
    assert(creates == 1 && enables == 1);
    assert(lastTarget == lookupAddress && lastEnabled == lookupAddress);
    assert(lastReplacement == reinterpret_cast<void*>(RtlImageDirectoryEntryToDataStub));
    // Both inlined entry lookup and public table lookup request the mapped image
    // exception directory. Every other module/directory/mapping mode forwards.
    for (DWORD64 module : {0ull, 0x1000ull, 0x2000ull})
    for (WORD index : {WORD(0), WORD(3), WORD(9)})
    for (BOOL mapped : {0, 1})
    {
        ULONG length = 0; directoryCalls = 0;
        auto handle = reinterpret_cast<HMODULE>(module);
        auto result = RtlImageDirectoryEntryToDataStub(handle, mapped, index, &length);
        bool override = module == 0x1000 && index == IMAGE_DIRECTORY_ENTRY_EXCEPTION && mapped;
        assert(result == (override ? static_cast<void*>(functions) : reinterpret_cast<void*>(0xDDD)));
        assert(length == (override ? sizeof(functions) : 55));
        assert(directoryCalls == (override ? 0 : 1));
        if (!override)
            assert(directoryModule == handle && directoryMapped == mapped && directoryIndex == index && directoryLength == &length);
    }
    g_originalLookupDownLevel = originalLookup;
    assert(scans == 0 && versionChecks == 0 && queries == 0);
    for (DWORD64 pc : {0ull, 0xFFFull, 0x1000ull, 0x1FFFull, 0x2000ull, 0x2001ull})
    {
        DWORD64 base = 0; ULONG length = 0;
        void* result = RtlpxLookupFunctionTableOverrideDownLevel(reinterpret_cast<void*>(pc), &base, &length);
        assert(forwardedAddress == reinterpret_cast<void*>(pc));
        assert(forwardedBase == &base && forwardedLength == &length);
        bool inside = pc >= 0x1000 && pc < 0x2000;
        assert(result == (inside ? static_cast<void*>(functions) : reinterpret_cast<void*>(0xEEE)));
        assert(base == (inside ? 0x1000 : 0xABC));
        assert(length == (inside ? sizeof(functions) : 9)); // Wine reports table size in BYTES.
    }
    reset(); exportPresent = false;
    try { CoreRT_SetupSEHHandler(reinterpret_cast<void*>(0x1000), reinterpret_cast<void*>(0x2000), functions, 3); assert(false); }
    catch (const std::runtime_error&) { assert(creates == 0 && enables == 0 && queries == 0 && scans == 0); }
    reset(); createStatus = 5;
    try { CoreRT_SetupSEHHandler(reinterpret_cast<void*>(0x1000), reinterpret_cast<void*>(0x2000), functions, 3); assert(false); }
    catch (const std::runtime_error&) { assert(creates == 1 && enables == 0 && queries == 0 && scans == 0); }
    reset(); enableStatus = 6;
    try { CoreRT_SetupSEHHandler(reinterpret_cast<void*>(0x1000), reinterpret_cast<void*>(0x2000), functions, 3); assert(false); }
    catch (const std::runtime_error&) { assert(creates == 1 && enables == 1 && queries == 0 && scans == 0); }
    reset(); wine = false;
    CoreRT_SetupSEHHandler(reinterpret_cast<void*>(0x1000), reinterpret_cast<void*>(0x2000), functions, 3);
    assert(scans == 1 && versionChecks == 1 && creates == 1 && enables == 1);
    assert(lastTarget == reinterpret_cast<void*>(0x6000) && lastEnabled == MH_ALL_HOOKS);
    std::puts("PASS: Wine early directory-hook branch; 18 module/directory/mapping combinations; byte length; six downlevel boundary addresses; missing export/create/enable failures; native Windows branch preserved (mock APIs only).");
}
'''
with tempfile.TemporaryDirectory(prefix='fivem-seh-validation-') as tmp:
    cpp = Path(tmp) / 'seh.cpp'
    binary = Path(tmp) / 'seh'
    cpp.write_text('#include <cwchar>\n' + prelude + production + tests)
    subprocess.run([os.environ.get('CXX', 'g++'), '-std=c++17', '-Wall', '-Wextra',
                    '-Wno-unused-variable', '-Wno-unused-parameter', '-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer', '-g', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
