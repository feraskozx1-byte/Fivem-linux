/* No SDK, CRT, patching or Wine identity hooks. x64 Windows diagnostics only. */
typedef unsigned char U8;
typedef unsigned short U16;
typedef unsigned int U32;
typedef unsigned long long U64;
typedef unsigned long long UPTR;
typedef long LONG;
typedef int BOOL;
typedef void *HANDLE;
typedef void *HMODULE;
typedef void *FARPROC;
typedef const unsigned short *LPCWSTR;
#define DLLIMPORT __declspec(dllimport)
#define NOINLINE __declspec(noinline)
#define STD_OUTPUT_HANDLE ((U32)-11)
#define CONTINUE_SEARCH 0
#define FROM_ADDRESS_UNCHANGED 6u
#define LOAD_WITH_ALTERED_SEARCH_PATH 8u

struct ExceptionRecord {
    U32 code, flags;
    struct ExceptionRecord *nested;
    void *address;
    U32 parameter_count;
    UPTR parameters[15];
};
struct ExceptionPointers { struct ExceptionRecord *record; void *context; };
/* Windows x64 MEMORY_BASIC_INFORMATION: implicit DWORD padding at +20. */
struct MemoryBasicInformation {
    void *base_address;
    void *allocation_base;
    U32 allocation_protect;
    UPTR region_size;
    U32 state;
    U32 protect;
    U32 type;
};
_Static_assert(sizeof(struct MemoryBasicInformation) == 48, "x64 MBI size");

typedef LONG (*ExceptionHandler)(struct ExceptionPointers *);
DLLIMPORT HANDLE GetStdHandle(U32);
DLLIMPORT BOOL WriteFile(HANDLE, const void *, U32, U32 *, void *);
DLLIMPORT void ExitProcess(U32);
DLLIMPORT HANDLE CreateFileW(LPCWSTR, U32, U32, void *, U32, U32, HANDLE);
DLLIMPORT BOOL FlushFileBuffers(HANDLE);
DLLIMPORT BOOL CloseHandle(HANDLE);
DLLIMPORT U32 GetLastError(void);
DLLIMPORT LPCWSTR GetCommandLineW(void);
DLLIMPORT HMODULE GetModuleHandleW(LPCWSTR);
DLLIMPORT FARPROC GetProcAddress(HMODULE, const char *);
DLLIMPORT HMODULE LoadLibraryExW(LPCWSTR, HANDLE, U32);
DLLIMPORT void *AddVectoredExceptionHandler(U32, ExceptionHandler);
DLLIMPORT BOOL GetModuleHandleExA(U32, const char *, HMODULE *);
DLLIMPORT U32 GetModuleFileNameA(HMODULE, char *, U32);
DLLIMPORT UPTR VirtualQuery(const void *, struct MemoryBasicInformation *, UPTR);

static HANDLE output;
static HANDLE disk_output;
static U32 disk_write_failed;
static volatile LONG handling_exception;
static volatile U32 exception_count;
static volatile U32 phase;
static volatile U32 phase_exceptions[6];
static const unsigned short old_core_path[] = L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Run-Adhesive-Test\\CoreRT.dll";
static const unsigned short new_core_path[] = L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Run-CoreRT-Test\\CoreRT.dll";
static const unsigned short adhesive_path[] = L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Run-Adhesive-Test\\adhesive.dll";

static void put_n(const char *s, U32 n)
{
    U32 written;
    if (n) WriteFile(output, s, n, &written, (void *)0);
    if (n && disk_output) {
        if (!WriteFile(disk_output, s, n, &written, (void *)0) || written != n)
            disk_write_failed = 1;
    }
}
static void put(const char *s)
{
    U32 n = 0;
    while (s[n]) ++n;
    put_n(s, n);
}
static void hex(UPTR value)
{
    const char digits[] = "0123456789abcdef";
    char b[18];
    U32 i;
    b[0] = '0'; b[1] = 'x';
    for (i = 0; i < 16; ++i) b[2 + i] = digits[(value >> (60 - i * 4)) & 15];
    put_n(b, 18);
}
static void dec(U32 value)
{
    char b[10]; U32 n = 0;
    do { b[9 - n++] = (char)('0' + value % 10); value /= 10; } while (value);
    put_n(b + 10 - n, n);
}
static void field(const char *name, UPTR value)
{
    put(name); hex(value); put("\r\n");
}
static void finish(U32 result)
{
    if (disk_write_failed) result = 6;
    put("PROBE_EXIT_CODE="); dec(result); put("\r\n");
    if (disk_output) {
        if (!FlushFileBuffers(disk_output)) result = 6;
        if (!CloseHandle(disk_output)) result = 6;
        disk_output = (HANDLE)0;
    }
    ExitProcess(result);
}
static LONG exception_logger(struct ExceptionPointers *p)
{
    HMODULE module = (HMODULE)0;
    char path[768];
    U32 n;
    ++exception_count;
    if (phase < 6) ++phase_exceptions[phase];
    if (handling_exception) return CONTINUE_SEARCH;
    handling_exception = 1;
    put("VEH phase="); dec(phase); put(" code="); hex(p->record->code);
    put(" address="); hex((UPTR)p->record->address);
    if (GetModuleHandleExA(FROM_ADDRESS_UNCHANGED, (const char *)p->record->address, &module)) {
        put(" module_base="); hex((UPTR)module);
        put(" offset="); hex((UPTR)p->record->address - (UPTR)module);
        n = GetModuleFileNameA(module, path, (U32)sizeof(path));
        if (n && n < sizeof(path)) { put(" module="); put_n(path, n); }
    }
    if (p->record->parameter_count >= 2 &&
        (p->record->code == 0xc0000005u || p->record->code == 0xc0000006u)) {
        put(" access_kind="); hex(p->record->parameters[0]);
        struct MemoryBasicInformation mbi;
        UPTR queried;
        put(" target="); hex(p->record->parameters[1]);
        queried = VirtualQuery((void *)p->record->parameters[1], &mbi, sizeof(mbi));
        put(" VirtualQuery_bytes="); hex(queried);
        if (queried == sizeof(mbi)) {
            put(" region_base="); hex((UPTR)mbi.base_address);
            put(" region_size="); hex(mbi.region_size);
            put(" allocation_base="); hex((UPTR)mbi.allocation_base);
            put(" allocation_protect="); hex(mbi.allocation_protect);
            put(" State="); hex(mbi.state);
            put(" Protect="); hex(mbi.protect);
            put(" Type="); hex(mbi.type);
        } else {
            put(" VirtualQuery_error="); hex(GetLastError());
        }
    }
    put("\r\n");
    handling_exception = 0;
    return CONTINUE_SEARCH;
}

/* Parse only a single explicit mode. Never print the incoming command line. */
static int argument_is(LPCWSTR p, LPCWSTR wanted)
{
    U32 i;
    for (i = 0; wanted[i]; ++i) if (p[i] != wanted[i]) return 0;
    p += i;
    while (*p == ' ' || *p == '\t') ++p;
    return !*p;
}
static int mode(void)
{
    LPCWSTR p = GetCommandLineW();
    if (*p == '"') { ++p; while (*p && *p != '"') ++p; if (*p) ++p; }
    else while (*p && *p != ' ' && *p != '\t') ++p;
    while (*p == ' ' || *p == '\t') ++p;
    if (!*p) return -1;
    if (argument_is(p, L"--old-core")) return 1;
    if (argument_is(p, L"--new-core")) return 2;
    return -1;
}

void mainCRTStartup(void)
{
    int selected;
    U32 error;
    HMODULE module;
    output = GetStdHandle(STD_OUTPUT_HANDLE);
    selected = mode();
    /* CREATE_NEW preserves any earlier measurement; all disk output stays in C:. */
    if (selected < 0) {
        put("Usage: loader-probe.exe --old-core|--new-core\r\n"); ExitProcess(64);
    }
    disk_output = CreateFileW(selected == 2 ? L"C:\\adhesive-probe-v4-new-core.txt" :
        L"C:\\adhesive-probe-v4-old-core.txt",
        0x40000000u, 1u, (void *)0, 1u, 0x80u, (HANDLE)0);
    if (disk_output == (HANDLE)(UPTR)-1) {
        error = GetLastError(); disk_output = (HANDLE)0;
        field("CreateFileW_error=", error); ExitProcess(5);
    }
    put("loader-probe v4 x64 no-CRT; VEH logs only, always CONTINUE_SEARCH\r\n");
    if (!AddVectoredExceptionHandler(1, exception_logger)) {
        field("AddVectoredExceptionHandler_error=", GetLastError()); finish(4);
    }
    put(selected == 2 ? "MODE=new-core\r\n" : "MODE=old-core\r\n");
    put("No EarlyMode_Init, component factory or Wine identity hook invoked\r\n");
    phase = 5;
    module = LoadLibraryExW(selected == 2 ? new_core_path : old_core_path,
        (HANDLE)0, LOAD_WITH_ALTERED_SEARCH_PATH);
    error = module ? 0 : GetLastError();
    phase = 0;
    field("preload_core_module=", (UPTR)module);
    put("preload_core_error="); dec(error); put("\r\n");
    put("core_exception_count="); dec(phase_exceptions[5]); put("\r\n");
    if (!module) { put("CORE_RESULT=failed\r\n"); finish(11); }
    {
        char path[768];
        U32 n = GetModuleFileNameA(module, path, (U32)sizeof(path));
        if (n && n < sizeof(path)) {
            put("resolved_core_path="); put_n(path, n); put("\r\n");
        } else {
            field("GetModuleFileNameA_error=", GetLastError()); finish(12);
        }
    }
    put("LoadLibraryExW flags=LOAD_WITH_ALTERED_SEARCH_PATH\r\n");
    phase = 4;
    module = LoadLibraryExW(adhesive_path, (HANDLE)0, LOAD_WITH_ALTERED_SEARCH_PATH);
    error = module ? 0 : GetLastError();
    phase = 0;
    field("adhesive_module=", (UPTR)module);
    put("LoadLibraryExW_error="); dec(error); put("\r\n");
    put("loader_exception_count="); dec(phase_exceptions[4]); put("\r\n");
    put(module ? "LOAD_RESULT=success; library load only\r\n" : "LOAD_RESULT=failed\r\n");
    /* Do not invoke CreateComponent, connect, unload forcibly or handle exceptions. */
    finish(module ? 0 : 10);
}
