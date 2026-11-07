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
struct RuntimeFunction { U32 begin, end, unwind; };

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

typedef void *(*LookupTable)(UPTR, U64 *, U32 *);
typedef void *(*DirectoryData)(void *, unsigned char, U16, U32 *);
typedef struct RuntimeFunction *(*LookupEntry)(UPTR, U64 *, void *);

static HANDLE output;
static HANDLE disk_output;
static U32 disk_write_failed;
static volatile LONG handling_exception;
static volatile U32 exception_count;
static volatile U32 phase;
static volatile U32 phase_exceptions[6];
static const unsigned short core_path[] = L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Run-Adhesive-Test\\CoreRT.dll";
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
        put(" target="); hex(p->record->parameters[1]);
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
    if (!*p) return 0;
    if (argument_is(p, L"--adhesive")) return 1;
    if (argument_is(p, L"--adhesive-initialized")) return 2;
    return -1;
}

static NOINLINE U32 check_abi(void *pc)
{
    HMODULE self = GetModuleHandleW((LPCWSTR)0);
    HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
    LookupTable table_fn = (LookupTable)GetProcAddress(ntdll, "RtlLookupFunctionTable");
    DirectoryData directory_fn = (DirectoryData)GetProcAddress(ntdll, "RtlImageDirectoryEntryToData");
    LookupEntry entry_fn = (LookupEntry)GetProcAddress(ntdll, "RtlLookupFunctionEntry");
    U32 directory_bytes = 0, table_length = 0;
    U64 table_base = 0, entry_base = 0;
    void *directory_table, *lookup_table;
    struct RuntimeFunction *entry;
    field("self_base=", (UPTR)self);
    field("control_pc=", (UPTR)pc);
    field("RtlLookupFunctionTable=", (UPTR)table_fn);
    field("RtlImageDirectoryEntryToData=", (UPTR)directory_fn);
    field("RtlLookupFunctionEntry=", (UPTR)entry_fn);
    if (!table_fn || !directory_fn || !entry_fn) {
        put("ABI_RESULT=required_export_missing\r\n"); return 2;
    }
    phase = 1;
    directory_table = directory_fn(self, 1, 3, &directory_bytes);
    phase = 2;
    lookup_table = table_fn((UPTR)pc, &table_base, &table_length);
    phase = 3;
    entry = entry_fn((UPTR)pc, &entry_base, (void *)0);
    phase = 0;
    field("directory_table=", (UPTR)directory_table);
    put("directory_bytes="); dec(directory_bytes); put("\r\n");
    put("runtime_function_size="); dec(sizeof(struct RuntimeFunction)); put("\r\n");
    put("directory_entry_count="); dec(directory_bytes / sizeof(struct RuntimeFunction)); put("\r\n");
    field("lookup_table=", (UPTR)lookup_table);
    field("lookup_image_base=", (UPTR)table_base);
    put("lookup_length="); dec(table_length); put("\r\n");
    field("lookup_entry=", (UPTR)entry);
    field("entry_image_base=", (UPTR)entry_base);
    if (!directory_table || !directory_bytes || !lookup_table || !entry ||
        directory_bytes % sizeof(struct RuntimeFunction) ||
        directory_table != lookup_table || table_base != (U64)(UPTR)self ||
        entry_base != (U64)(UPTR)self) {
        put("ABI_RESULT=table_or_entry_mismatch\r\n"); return 3;
    }
    if ((UPTR)entry < (UPTR)directory_table ||
        (UPTR)entry >= (UPTR)directory_table + directory_bytes) {
        put("ABI_RESULT=entry_outside_table\r\n"); return 3;
    }
    if (table_length == directory_bytes / sizeof(struct RuntimeFunction)) {
        put("ABI_RESULT=lookup_length_is_entry_count\r\n"); return 0;
    }
    if (table_length == directory_bytes) {
        put("ABI_RESULT=lookup_length_is_byte_size\r\n"); return 0;
    }
    put("ABI_RESULT=unrecognized_length_semantics\r\n"); return 3;
}

void mainCRTStartup(void)
{
    int selected;
    U32 result, error;
    HMODULE module;
    output = GetStdHandle(STD_OUTPUT_HANDLE);
    selected = mode();
    /* CREATE_NEW preserves any earlier measurement; all disk output stays in C:. */
    disk_output = CreateFileW(selected == 2 ? L"C:\\compat-probe-adhesive-initialized.txt" :
        selected == 1 ? L"C:\\compat-probe-adhesive.txt" : L"C:\\compat-probe-abi.txt",
        0x40000000u, 1u, (void *)0, 1u, 0x80u, (HANDLE)0);
    if (disk_output == (HANDLE)(UPTR)-1) {
        error = GetLastError(); disk_output = (HANDLE)0;
        field("CreateFileW_error=", error); ExitProcess(5);
    }
    put("loader-probe v3 x64 no-CRT; VEH logs only, always CONTINUE_SEARCH\r\n");
    if (!AddVectoredExceptionHandler(1, exception_logger)) {
        field("AddVectoredExceptionHandler_error=", GetLastError()); finish(4);
    }
    if (selected < 0) { put("Usage: loader-probe.exe [--adhesive|--adhesive-initialized]\r\n"); finish(64); }
    if (!selected) {
        put("MODE=abi; no game DLL loaded\r\n");
        result = check_abi((void *)&mainCRTStartup);
        put("exception_count="); dec(exception_count); put("\r\n");
        finish(result);
    }
    if (selected == 2) {
        put("MODE=adhesive-initialized; preload ordinary CoreRT globals first\r\n");
        put("No EarlyMode_Init, component factory or Wine identity hook invoked\r\n");
        phase = 5;
        module = LoadLibraryExW(core_path, (HANDLE)0, LOAD_WITH_ALTERED_SEARCH_PATH);
        error = module ? 0 : GetLastError();
        phase = 0;
        field("preload_core_module=", (UPTR)module);
        put("preload_core_error="); dec(error); put("\r\n");
        put("core_exception_count="); dec(phase_exceptions[5]); put("\r\n");
        if (!module) { put("CORE_RESULT=failed\r\n"); finish(11); }
    } else {
        put("MODE=adhesive; fixed official-reference copy, unmodified loader\r\n");
    }
    put("LoadLibraryExW flags=LOAD_WITH_ALTERED_SEARCH_PATH\r\n");
    phase = 4;
    module = LoadLibraryExW(adhesive_path, (HANDLE)0, LOAD_WITH_ALTERED_SEARCH_PATH);
    error = module ? 0 : GetLastError();
    phase = 0;
    field("adhesive_module=", (UPTR)module);
    put("LoadLibraryExW_error="); dec(error); put("\r\n");
    put("loader_exception_count="); dec(phase_exceptions[4]); put("\r\n");
    put(module ? "LOAD_RESULT=success; not evidence of server authentication\r\n" : "LOAD_RESULT=failed\r\n");
    /* Do not invoke CreateComponent, connect, unload forcibly or handle exceptions. */
    finish(module ? 0 : 10);
}
