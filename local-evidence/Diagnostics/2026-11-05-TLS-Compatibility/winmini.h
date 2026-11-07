#ifndef WINMINI_H
#define WINMINI_H
typedef unsigned char U8;
typedef unsigned short U16;
typedef unsigned int U32;
typedef unsigned long long U64;
typedef long long I64;
typedef long LONG;
typedef int BOOL;
typedef void *HANDLE;
typedef void *HMODULE;
typedef void *FARPROC;
typedef unsigned long long SIZE;
#define IMP __declspec(dllimport)
#define EXPORT __declspec(dllexport)
#define NOINLINE __declspec(noinline)
#define NULL ((void*)0)
struct MBI { void *base,*allocation;U32 allocation_protect;SIZE region_size;U32 state,protect,type; };
struct IOSB { union {LONG status;void *pointer;};SIZE information; };
struct STANDARD {I64 allocation,end;U32 links;U8 deleting,directory;};
_Static_assert(sizeof(struct MBI)==48,"MBI x64");
_Static_assert(sizeof(struct IOSB)==16,"IOSB x64");
_Static_assert(sizeof(struct STANDARD)==24,"FILE_STANDARD_INFORMATION");
IMP HANDLE GetStdHandle(U32);
IMP BOOL WriteFile(HANDLE,const void*,U32,U32*,void*);
IMP HANDLE CreateFileW(const U16*,U32,U32,void*,U32,U32,HANDLE);
IMP BOOL CloseHandle(HANDLE);
IMP BOOL DeleteFileW(const U16*);
IMP BOOL FlushFileBuffers(HANDLE);
IMP void ExitProcess(U32);
IMP U32 GetLastError(void);
IMP HMODULE GetModuleHandleW(const U16*);
IMP FARPROC GetProcAddress(HMODULE,const char*);
IMP HMODULE LoadLibraryW(const U16*);
IMP BOOL FreeLibrary(HMODULE);
IMP U32 GetModuleFileNameW(HMODULE,U16*,U32);
IMP void *VirtualAlloc(void*,SIZE,U32,U32);
IMP BOOL VirtualFree(void*,SIZE,U32);
IMP BOOL VirtualProtect(void*,SIZE,U32,U32*);
IMP SIZE VirtualQuery(const void*,struct MBI*,SIZE);
IMP void RaiseException(U32,U32,U32,const SIZE*);
#endif
