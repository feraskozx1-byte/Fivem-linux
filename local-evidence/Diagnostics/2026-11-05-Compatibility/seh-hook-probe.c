/* Disposable-process x64 Windows SEH directory-hook strategy diagnostic.
 * No game/security DLLs, Wine identity hooks, CRT, SDK, or MinHook dependency.
 * This patches ONLY this probe process's ntdll memory after an exact prologue
 * check, tests copied unwind-table lookup, then restores the original bytes.
 * It is NOT a MinHook test, rebuilt CoreRT test, or exception-unwinding test.
 */
typedef unsigned char U8;
typedef unsigned short U16;
typedef unsigned int U32;
typedef unsigned long long U64;
typedef unsigned long long UPTR;
typedef int BOOL;
typedef void *HANDLE;
typedef void *HMODULE;
typedef void *FARPROC;
typedef const unsigned short *LPCWSTR;
#define DLLIMPORT __declspec(dllimport)
#define NOINLINE __declspec(noinline)
#define STD_OUTPUT_HANDLE ((U32)-11)
#define PAGE_READONLY 2u
#define PAGE_READWRITE 4u
#define PAGE_EXECUTE_READ 0x20u
#define PAGE_EXECUTE_READWRITE 0x40u
#define MEM_COMMIT_RESERVE 0x3000u
#define MEM_RELEASE 0x8000u
#define EXCEPTION_DIRECTORY 3u
#define PROLOGUE_SIZE 15u

DLLIMPORT HANDLE GetStdHandle(U32);
DLLIMPORT BOOL WriteFile(HANDLE, const void *, U32, U32 *, void *);
DLLIMPORT void ExitProcess(U32);
DLLIMPORT HANDLE CreateFileW(LPCWSTR, U32, U32, void *, U32, U32, HANDLE);
DLLIMPORT BOOL FlushFileBuffers(HANDLE);
DLLIMPORT BOOL CloseHandle(HANDLE);
DLLIMPORT U32 GetLastError(void);
DLLIMPORT HMODULE GetModuleHandleW(LPCWSTR);
DLLIMPORT FARPROC GetProcAddress(HMODULE, const char *);
DLLIMPORT void *VirtualAlloc(void *, UPTR, U32, U32);
DLLIMPORT BOOL VirtualProtect(void *, UPTR, U32, U32 *);
DLLIMPORT BOOL VirtualFree(void *, UPTR, U32);
DLLIMPORT BOOL FlushInstructionCache(HANDLE, const void *, UPTR);
DLLIMPORT HANDLE GetCurrentProcess(void);

struct RuntimeFunction { U32 begin, end, unwind; };
typedef void *(*DirectoryData)(HMODULE, BOOL, U16, U32 *);
typedef void *(*LookupTable)(UPTR, U64 *, U32 *);
typedef struct RuntimeFunction *(*LookupEntry)(UPTR, U64 *, void *);
struct DirectoryObservation { HMODULE module; BOOL mapped; U16 directory; void *data; U32 bytes; };

static HANDLE output, disk_output;
static U32 disk_failed;
static HMODULE own_module;
static U8 *directory_target, *trampoline_memory, *table_copy;
static U32 copy_bytes, original_protection;
static BOOL target_modified;
static DirectoryData original_directory;
static U32 override_calls, forward_calls;
static const U8 expected_prologue[PROLOGUE_SIZE] = {
    0x55, 0x41, 0x54, 0x57, 0x56, 0x53, 0x48, 0x83,
    0xec, 0x20, 0x48, 0x8d, 0x6c, 0x24, 0x20
};

static void put_n(const char *s, U32 n)
{
    U32 written;
    if (n) WriteFile(output, s, n, &written, (void *)0);
    if (n && disk_output &&
        (!WriteFile(disk_output, s, n, &written, (void *)0) || written != n))
        disk_failed = 1;
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
    char buffer[18];
    U32 i;
    buffer[0] = '0'; buffer[1] = 'x';
    for (i = 0; i < 16; ++i) buffer[2 + i] = digits[(value >> (60 - i * 4)) & 15];
    put_n(buffer, 18);
}
static void field(const char *name, UPTR value)
{
    put(name); hex(value); put("\r\n");
}
static void copy_memory(U8 *destination, const U8 *source, U32 bytes)
{
    U32 i;
    for (i = 0; i < bytes; ++i) destination[i] = source[i];
}
static BOOL same_memory(const U8 *a, const U8 *b, U32 bytes)
{
    U32 i;
    for (i = 0; i < bytes; ++i) if (a[i] != b[i]) return 0;
    return 1;
}
/* 14-byte RIP-indirect absolute jump. No argument or scratch register clobber. */
static void absolute_jump(U8 *destination, const void *target)
{
    U32 i;
    UPTR address = (UPTR)target;
    destination[0] = 0xff; destination[1] = 0x25;
    for (i = 2; i < 6; ++i) destination[i] = 0;
    for (i = 0; i < 8; ++i) destination[6 + i] = (U8)(address >> (i * 8));
}
static BOOL restore_target(void)
{
    U32 temporary, ignored;
    BOOL flushed, protected;
    if (!target_modified) return 1;
    if (!VirtualProtect(directory_target, PROLOGUE_SIZE, PAGE_EXECUTE_READWRITE, &temporary)) {
        field("restore_VirtualProtect_error=", GetLastError()); return 0;
    }
    copy_memory(directory_target, expected_prologue, PROLOGUE_SIZE);
    flushed = FlushInstructionCache(GetCurrentProcess(), directory_target, PROLOGUE_SIZE);
    protected = VirtualProtect(directory_target, PROLOGUE_SIZE, original_protection, &ignored);
    target_modified = 0;
    if (!flushed || !protected || !same_memory(directory_target, expected_prologue, PROLOGUE_SIZE)) {
        put("RESTORE_RESULT=failed\r\n"); return 0;
    }
    put("RESTORE_RESULT=original_bytes_and_protection_restored\r\n");
    return 1;
}
static void finish(U32 result)
{
    if (!restore_target()) result = 40;
    if (trampoline_memory && !target_modified) {
        if (!VirtualFree(trampoline_memory, 0, MEM_RELEASE)) result = 41;
        trampoline_memory = (U8 *)0;
    }
    if (table_copy && !target_modified) {
        if (!VirtualFree(table_copy, 0, MEM_RELEASE)) result = 41;
        table_copy = (U8 *)0;
    }
    if (disk_failed) result = 6;
    field("PROBE_EXIT_CODE=", result);
    if (disk_output) {
        if (!FlushFileBuffers(disk_output)) result = 6;
        if (!CloseHandle(disk_output)) result = 6;
        disk_output = (HANDLE)0;
    }
    ExitProcess(result);
}
static void require(BOOL condition, const char *failure, U32 code)
{
    if (!condition) { put("FAIL="); put(failure); put("\r\n"); finish(code); }
}
/* Same scope/byte-length semantics as final CoreRT source stub. */
static NOINLINE void *directory_stub(HMODULE module, BOOL mapped_as_image, U16 directory, U32 *bytes)
{
    if (module == own_module && mapped_as_image && directory == EXCEPTION_DIRECTORY) {
        ++override_calls;
        *bytes = copy_bytes;
        return table_copy;
    }
    ++forward_calls;
    return original_directory(module, mapped_as_image, directory, bytes);
}
/* Force a real non-leaf function with valid PE unwind metadata. */
static NOINLINE U32 control_function(U32 value)
{
    volatile U32 local[4];
    local[0] = value;
    return local[0] + GetLastError();
}
static BOOL entry_in_table(struct RuntimeFunction *entry, const U8 *table, U32 bytes, UPTR pc)
{
    UPTR address = (UPTR)entry;
    if (!entry || address < (UPTR)table || address >= (UPTR)table + bytes ||
        (address - (UPTR)table) % sizeof(*entry)) return 0;
    return pc >= (UPTR)own_module + entry->begin && pc < (UPTR)own_module + entry->end;
}

void mainCRTStartup(void)
{
    HMODULE ntdll;
    DirectoryData directory_fn;
    LookupTable table_fn;
    LookupEntry entry_fn;
    void *original_table, *table;
    struct RuntimeFunction *entry;
    U64 image_base;
    U32 bytes, original_bytes, temporary, ignored, i;
    UPTR pc = (UPTR)&control_function;
    struct DirectoryObservation forwarding[3];

    output = GetStdHandle(STD_OUTPUT_HANDLE);
    /* CREATE_NEW preserves earlier runs and puts all output inside the probe prefix. */
    disk_output = CreateFileW(L"C:\\compat-probe-seh-hook.txt", 0x40000000u, 1u,
        (void *)0, 1u, 0x80u, (HANDLE)0);
    if (disk_output == (HANDLE)(UPTR)-1) {
        disk_output = (HANDLE)0;
        field("CreateFileW_error=", GetLastError()); ExitProcess(5);
    }
    put("seh-hook-probe v1; own-process ntdll hook strategy only; NOT MinHook/CoreRT/unwind test\r\n");
    own_module = GetModuleHandleW((LPCWSTR)0);
    ntdll = GetModuleHandleW(L"ntdll.dll");
    directory_fn = (DirectoryData)GetProcAddress(ntdll, "RtlImageDirectoryEntryToData");
    table_fn = (LookupTable)GetProcAddress(ntdll, "RtlLookupFunctionTable");
    entry_fn = (LookupEntry)GetProcAddress(ntdll, "RtlLookupFunctionEntry");
    require(own_module && ntdll && directory_fn && table_fn && entry_fn, "required_export_missing", 10);
    directory_target = (U8 *)directory_fn;
    field("self_base=", (UPTR)own_module);
    field("directory_target=", (UPTR)directory_target);
    field("control_pc=", pc);
    require(same_memory(directory_target, expected_prologue, PROLOGUE_SIZE), "ntdll_prologue_mismatch_NO_PATCH", 11);
    put("PROLOGUE_RESULT=exact_15_bytes_match\r\n");
    (void)control_function(1);

    original_bytes = 0;
    original_table = directory_fn(own_module, 1, EXCEPTION_DIRECTORY, &original_bytes);
    require(original_table && original_bytes && original_bytes <= 0x100000u &&
        original_bytes % sizeof(struct RuntimeFunction) == 0, "invalid_own_exception_directory", 12);
    field("original_table=", (UPTR)original_table);
    field("original_table_bytes=", original_bytes);
    image_base = 0; bytes = 0;
    table = table_fn(pc, &image_base, &bytes);
    require(table == original_table && bytes == original_bytes && image_base == (U64)(UPTR)own_module,
        "baseline_table_lookup_mismatch", 13);
    image_base = 0;
    entry = entry_fn(pc, &image_base, (void *)0);
    require(image_base == (U64)(UPTR)own_module && entry_in_table(entry, original_table, original_bytes, pc),
        "baseline_entry_lookup_mismatch", 14);
    field("baseline_entry=", (UPTR)entry);

    /* Observe three requests which must retain exact original return/size. */
    forwarding[0].module = own_module; forwarding[0].mapped = 1; forwarding[0].directory = 1;
    forwarding[1].module = ntdll; forwarding[1].mapped = 1; forwarding[1].directory = EXCEPTION_DIRECTORY;
    forwarding[2].module = own_module; forwarding[2].mapped = 0; forwarding[2].directory = EXCEPTION_DIRECTORY;
    for (i = 0; i < 3; ++i) {
        forwarding[i].bytes = 0x11223344u;
        forwarding[i].data = directory_fn(forwarding[i].module, forwarding[i].mapped,
            forwarding[i].directory, &forwarding[i].bytes);
    }

    copy_bytes = original_bytes;
    table_copy = (U8 *)VirtualAlloc((void *)0, copy_bytes, MEM_COMMIT_RESERVE, PAGE_READWRITE);
    require(table_copy && table_copy != (U8 *)original_table, "copy_allocation_failed", 15);
    copy_memory(table_copy, (const U8 *)original_table, copy_bytes);
    require(VirtualProtect(table_copy, copy_bytes, PAGE_READONLY, &ignored), "copy_readonly_failed", 16);
    field("distinct_table_copy=", (UPTR)table_copy);

    trampoline_memory = (U8 *)VirtualAlloc((void *)0, 4096, MEM_COMMIT_RESERVE, PAGE_READWRITE);
    require(trampoline_memory != (U8 *)0, "trampoline_allocation_failed", 17);
    copy_memory(trampoline_memory, expected_prologue, PROLOGUE_SIZE);
    absolute_jump(trampoline_memory + PROLOGUE_SIZE, directory_target + PROLOGUE_SIZE);
    require(VirtualProtect(trampoline_memory, 4096, PAGE_EXECUTE_READ, &temporary), "trampoline_protection_failed", 18);
    require(FlushInstructionCache(GetCurrentProcess(), trampoline_memory, PROLOGUE_SIZE + 14),
        "trampoline_cache_flush_failed", 19);
    original_directory = (DirectoryData)trampoline_memory;
    require(same_memory(directory_target, expected_prologue, PROLOGUE_SIZE), "prologue_changed_NO_PATCH", 20);
    require(VirtualProtect(directory_target, PROLOGUE_SIZE, PAGE_EXECUTE_READWRITE, &original_protection),
        "target_write_protection_failed", 21);
    target_modified = 1;
    absolute_jump(directory_target, (void *)&directory_stub);
    directory_target[14] = 0x90;
    require(FlushInstructionCache(GetCurrentProcess(), directory_target, PROLOGUE_SIZE), "target_cache_flush_failed", 22);
    require(VirtualProtect(directory_target, PROLOGUE_SIZE, original_protection, &ignored),
        "target_execute_protection_failed", 23);
    put("HOOK_RESULT=installed_in_probe_process_only\r\n");

    bytes = 0;
    table = directory_fn(own_module, 1, EXCEPTION_DIRECTORY, &bytes);
    require(table == table_copy && bytes == copy_bytes, "direct_directory_not_copy", 24);
    image_base = 0; bytes = 0;
    table = table_fn(pc, &image_base, &bytes);
    require(table == table_copy && bytes == copy_bytes && image_base == (U64)(UPTR)own_module,
        "exported_table_lookup_not_copy", 25);
    field("hooked_lookup_table=", (UPTR)table);
    field("hooked_table_bytes=", bytes);
    image_base = 0;
    entry = entry_fn(pc, &image_base, (void *)0);
    require(image_base == (U64)(UPTR)own_module && entry_in_table(entry, table_copy, copy_bytes, pc),
        "inlined_entry_lookup_not_copy", 26);
    field("hooked_lookup_entry=", (UPTR)entry);
    field("hooked_entry_base=", (UPTR)image_base);
    for (i = 0; i < 3; ++i) {
        bytes = 0x11223344u;
        table = directory_fn(forwarding[i].module, forwarding[i].mapped, forwarding[i].directory, &bytes);
        require(table == forwarding[i].data && bytes == forwarding[i].bytes, "forwarding_changed_return_or_size", 27);
    }
    field("override_calls=", override_calls);
    field("forward_calls=", forward_calls);
    require(override_calls >= 3 && forward_calls >= 3, "expected_hook_calls_not_observed", 28);
    put("STRATEGY_RESULT=direct_table_and_inlined_entry_use_distinct_copy; forwarding_matches_baseline\r\n");

    require(restore_target(), "restore_failed", 40);
    image_base = 0; bytes = 0;
    table = table_fn(pc, &image_base, &bytes);
    require(table == original_table && bytes == original_bytes && image_base == (U64)(UPTR)own_module,
        "post_restore_table_lookup_mismatch", 29);
    image_base = 0;
    entry = entry_fn(pc, &image_base, (void *)0);
    require(image_base == (U64)(UPTR)own_module && entry_in_table(entry, original_table, original_bytes, pc),
        "post_restore_entry_lookup_mismatch", 30);
    put("POST_RESTORE_RESULT=original_table_and_entry_recovered\r\n");
    finish(0);
}
