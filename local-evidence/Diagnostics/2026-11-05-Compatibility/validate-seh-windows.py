#!/usr/bin/env python3
"""Compile the production SEH setup/overrides to Windows AMD64 COFF.

Uses the exact pinned MinHook API header and actual LaunchMode.h. Only Win32
types/API declarations are substituted for the unavailable Windows SDK. This
is neither a complete CoreRT build nor a deployable replacement object.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / 'Original-PR4050-Source'
text = (SOURCE / 'code/client/citicore/SEHTableHandler.Win32.cpp').read_text()
start = text.index('struct FUNCTION_TABLE_DATA')
end = text.index('\n#else\nvoid DLL_EXPORT CoreRT_SetupSEHHandler', start)
fragment = text[start:end]
win32 = r'''
#pragma once
#define WINAPI __stdcall
#define NTAPI __stdcall
#define NULL 0
typedef void VOID;
typedef void* LPVOID;
typedef const wchar_t* LPCWSTR;
typedef const char* LPCSTR;
typedef void* HANDLE;
typedef void* HMODULE;
typedef void* PVOID;
typedef int BOOL;
typedef int INT;
typedef unsigned short WORD;
typedef unsigned long DWORD;
typedef unsigned long ULONG;
typedef long NTSTATUS;
typedef unsigned __int64 DWORD64;
typedef DWORD64* PDWORD64;
typedef ULONG* PULONG;
typedef unsigned __int64 SIZE_T;
typedef SIZE_T* PSIZE_T;
typedef __int64 (WINAPI* FARPROC)();
struct RUNTIME_FUNCTION { DWORD BeginAddress, EndAddress, UnwindData; };
typedef RUNTIME_FUNCTION* PRUNTIME_FUNCTION;
extern "C" HMODULE WINAPI GetModuleHandleW(LPCWSTR);
#define GetModuleHandle GetModuleHandleW
extern "C" FARPROC WINAPI GetProcAddress(HMODULE, LPCSTR);
extern "C" HANDLE WINAPI GetCurrentProcess();
#define IMAGE_DIRECTORY_ENTRY_EXCEPTION 3
'''
prelude = r'''
#include <MinHook.h>
extern "C" void* __cdecl memset(void*, int, SIZE_T);
extern "C" char* __cdecl getenv(const char*);
#include "LaunchMode.h"
#define DLL_EXPORT __declspec(dllexport)
struct DisableToolHelpScope { DisableToolHelpScope(); ~DisableToolHelpScope(); };
extern bool IsWindows8Point1OrGreater();
extern bool IsWindows8OrGreater();
enum { UD_Icall, UD_Ijmp };
extern void* FindCallFromAddress(void*, int = UD_Icall, bool = false);
__declspec(noreturn) void FatalError(const char*, ...);
extern void trace(const char*, ...);
'''
output = ROOT / 'build-validation'
output.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='fivem-seh-coff-') as temporary:
    path = Path(temporary)
    (path / 'windows.h').write_text(win32)
    (path / 'winternl.h').write_text('#pragma once\n')
    cpp = path / 'seh-fragment.cpp'
    cpp.write_text(prelude + fragment)
    obj = output / 'seh-fragment-diagnostic-x64.obj'
    args = ['clang-cl', '--target=x86_64-pc-windows-msvc', '/nologo', '/c',
            '/std:c++17', '/W4', '/WX', '/O2', '/GS-', '/Zl',
            # Original Windows path uses an established MSVC pointer extension.
            '/clang:-Wno-microsoft-cast', '/I' + str(path),
            '/I' + str(output / 'pinned'),
            '/I' + str(SOURCE / 'code/client/citicore'), str(cpp), '/Fo' + str(obj)]
    subprocess.run(args, check=True)
    header = subprocess.check_output(['llvm-readobj', '--file-headers', str(obj)], text=True)
    assert 'IMAGE_FILE_MACHINE_AMD64' in header, header
    symbols = subprocess.check_output(['llvm-nm', str(obj)], text=True)
    assert 'CoreRT_SetupSEHHandler' in symbols
    (output / 'seh-windows-compile.txt').write_text(
        'PASS: unmodified production SEH setup/overrides compiled to AMD64 Windows COFF.\n'
        'Pinned MinHook: citizenfx/minhook b03840395033006c888288ac00a4608d8e2684cf/include/MinHook.h\n'
        'Actual LaunchMode.h included. Win32 declarations substituted; no full SDK/link/runtime test.\n'
        'Original MSVC function-pointer extension accepted explicitly; remaining /W4 /WX checks enabled.\n'
        + header)
print('PASS: production SEH fragment compiled to Windows AMD64 COFF with pinned MinHook API; SDK/link remain untested')
