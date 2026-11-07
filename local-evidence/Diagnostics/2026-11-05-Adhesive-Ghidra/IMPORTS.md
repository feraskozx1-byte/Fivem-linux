# Adhesive public imports — local dependency audit

SHA256: `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`

Presence of an export is not proof it is implemented correctly. Line numbers refer to Phase2/private/fullhost-legacy-ui/wine.log. CRT API-set contracts are resolved to ucrtbase; this is not a missing-DLL finding. Delay imports are marked separately.

| DLL / contract | Kind | Imports | Host attach success line |
| --- | --- | ---: | ---: |
| KERNEL32.dll | Import | 141 | 10308 |
| USER32.dll | Import | 4 | 11099 |
| libuv.dll | Import | 9 | 18353 |
| SHELL32.dll | Import | 2 | 11158 |
| ADVAPI32.dll | Import | 4 | 10336 |
| v8-9.3.345.16.dll | Import | 48 | 19586 |
| CRYPT32.dll | Import | 13 | 11507 |
| WS2_32.dll | Import | 41 | 11591 |
| SHLWAPI.dll | Import | 1 | 11151 |
| WINMM.dll | Import | 1 | 13069 |
| citizen-resources-client.dll | Import | 52 | 19696 |
| rage-device-five.dll | Import | 1 | 19706 |
| gta-core-five.dll | Import | 3 | 19808 |
| rage-nutsnbolts-five.dll | Import | 2 | 19727 |
| net.dll | Import | 3 | 19822 |
| legitimacy.dll | Import | 1 | 18444 |
| net-tcp-server.dll | Import | 1 | 18384 |
| net-base.dll | Import | 5 | 18367 |
| citizen-resources-core.dll | Import | 5 | 19633 |
| vfs-core.dll | Import | 29 | 19608 |
| scripting-gta.dll | Import | 2 | 19669 |
| rage-scripting-five.dll | Import | 1 | 19662 |
| MSVCP140.dll | Import | 111 | 16756 |
| CONCRT140.dll | Import | 1 | 16754 |
| RPCRT4.dll | Import | 2 | 11113 |
| WINTRUST.dll | Import | 1 | 19826 |
| CFGMGR32.dll | Import | 2 | 12199 |
| IPHLPAPI.DLL | Import | 1 | 11889 |
| VCRUNTIME140.dll | Import | 22 | 16720 |
| VCRUNTIME140_1.dll | Import | 1 | 17198 |
| api-ms-win-crt-stdio-l1-1-0.dll | Import | 29 | 10330 |
| api-ms-win-crt-locale-l1-1-0.dll | Import | 2 | 10330 |
| api-ms-win-crt-heap-l1-1-0.dll | Import | 7 | 10330 |
| api-ms-win-crt-runtime-l1-1-0.dll | Import | 23 | 10330 |
| api-ms-win-crt-math-l1-1-0.dll | Import | 15 | 10330 |
| api-ms-win-crt-time-l1-1-0.dll | Import | 4 | 10330 |
| api-ms-win-crt-string-l1-1-0.dll | Import | 20 | 10330 |
| api-ms-win-crt-convert-l1-1-0.dll | Import | 9 | 10330 |
| api-ms-win-crt-environment-l1-1-0.dll | Import | 1 | 10330 |
| api-ms-win-crt-utility-l1-1-0.dll | Import | 2 | 10330 |
| api-ms-win-crt-filesystem-l1-1-0.dll | Import | 6 | 10330 |
| bcrypt.dll | Import | 1 | 11196 |
| OLEAUT32.dll | Import | 5 | 11130 |
| ole32.dll | DelayImport | 3 | 11127 |

## Exact symbol inventory

### KERNEL32.dll (Import)

```text
AcquireSRWLockExclusive
AcquireSRWLockShared
AreFileApisANSI
CancelIoEx
CloseHandle
CompareFileTime
ConvertFiberToThread
ConvertThreadToFiber
CopyFileW
CreateDirectoryW
CreateEventA
CreateEventW
CreateFiber
CreateFileMappingW
CreateFileW
CreateIoCompletionPort
CreateSemaphoreExW
CreateToolhelp32Snapshot
CreateWaitableTimerW
DeleteCriticalSection
DeleteFiber
DeleteFileW
DisableThreadLibraryCalls
EnterCriticalSection
ExitProcess
FindClose
FindFirstFileW
FindNextFileW
FlushInstructionCache
FormatMessageA
FormatMessageW
FreeLibrary
GetCommandLineW
GetConsoleMode
GetCurrentProcess
GetCurrentProcessId
GetCurrentThread
GetCurrentThreadId
GetEnvironmentVariableA
GetEnvironmentVariableW
GetFileAttributesExW
GetFileAttributesW
GetFileType
GetFullPathNameW
GetLastError
GetLocaleInfoEx
GetModuleFileNameW
GetModuleHandleA
GetModuleHandleExW
GetModuleHandleW
GetNativeSystemInfo
GetPrivateProfileIntW
GetPrivateProfileStringW
GetProcAddress
GetProcessAffinityMask
GetProcessHeap
GetProcessWorkingSetSize
GetQueuedCompletionStatus
GetStdHandle
GetSystemDirectoryW
GetSystemInfo
GetSystemTime
GetSystemTimeAsFileTime
GetThreadContext
GetTickCount
HeapAlloc
HeapCreate
HeapFree
HeapReAlloc
InitOnceBeginInitialize
InitOnceComplete
InitializeCriticalSectionAndSpinCount
InitializeCriticalSectionEx
InitializeSListHead
InterlockedPushEntrySList
IsDebuggerPresent
IsProcessorFeaturePresent
LeaveCriticalSection
LoadLibraryA
LoadLibraryExA
LoadLibraryW
LocalAlloc
LocalFree
MapViewOfFile
MoveFileExW
MoveFileW
MultiByteToWideChar
OpenEventA
OpenProcess
OpenThread
OutputDebugStringA
PostQueuedCompletionStatus
QueryFullProcessImageNameW
QueryPerformanceCounter
QueryPerformanceFrequency
QueueUserAPC
RaiseException
ReadConsoleA
ReadConsoleW
ReleaseSRWLockExclusive
ReleaseSRWLockShared
ReleaseSemaphore
ResetEvent
ResumeThread
RtlCaptureContext
RtlLookupFunctionEntry
RtlVirtualUnwind
SetConsoleMode
SetEvent
SetLastError
SetThreadContext
SetUnhandledExceptionFilter
SetWaitableTimer
Sleep
SleepEx
SuspendThread
SwitchToFiber
SystemTimeToFileTime
TerminateProcess
TerminateThread
Thread32First
Thread32Next
TlsAlloc
TlsFree
TlsGetValue
TlsSetValue
UnhandledExceptionFilter
UnmapViewOfFile
VerSetConditionMask
VerifyVersionInfoW
VirtualAlloc
VirtualFree
VirtualLock
VirtualProtect
VirtualQuery
VirtualUnlock
WaitForMultipleObjects
WaitForSingleObject
WaitForSingleObjectEx
WideCharToMultiByte
WriteFile
```

### USER32.dll (Import)

```text
GetProcessWindowStation
GetUserObjectInformationW
MessageBoxW
RegisterSuspendResumeNotification
```

### libuv.dll (Import)

```text
uv_async_init
uv_async_send
uv_close
uv_poll_init_socket
uv_poll_start
uv_poll_stop
uv_timer_init
uv_timer_start
uv_timer_stop
```

### SHELL32.dll (Import)

```text
CommandLineToArgvW
SHGetKnownFolderPath
```

### ADVAPI32.dll (Import)

```text
DeregisterEventSource
RegGetValueW
RegisterEventSourceW
ReportEventW
```

### v8-9.3.345.16.dll (Import)

```text
??0CreateParams@Isolate@v8@@QEAA@XZ
??0HandleScope@v8@@QEAA@PEAVIsolate@1@@Z
??0TryCatch@v8@@QEAA@PEAVIsolate@1@@Z
??0Utf8Value@String@v8@@QEAA@PEAVIsolate@2@V?$Local@VValue@v8@@@2@@Z
??1CreateParams@Isolate@v8@@QEAA@XZ
??1HandleScope@v8@@QEAA@XZ
??1Locker@v8@@QEAA@XZ
??1TryCatch@v8@@QEAA@XZ
??1Utf8Value@String@v8@@QEAA@XZ
?ByteLength@ArrayBufferView@v8@@QEAA_KXZ
?Call@Function@v8@@QEAA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VValue@v8@@@2@HQEAV52@@Z
?Compile@Script@v8@@SA?AV?$MaybeLocal@VScript@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VString@v8@@@2@PEAVScriptOrigin@2@@Z
?CopyContents@ArrayBufferView@v8@@QEAA_KPEAX_K@Z
?CreateHandle@HandleScope@v8@@KAPEA_KPEAVIsolate@internal@2@_K@Z
?Data@BackingStore@v8@@QEBAPEAXXZ
?DisposeGlobal@V8@v8@@CAXPEA_K@Z
?Enter@Context@v8@@QEAAXXZ
?Enter@Isolate@v8@@QEAAXXZ
?Exception@TryCatch@v8@@QEBA?AV?$Local@VValue@v8@@@2@XZ
?Exit@Context@v8@@QEAAXXZ
?Exit@Isolate@v8@@QEAAXXZ
?Get@Object@v8@@QEAA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VValue@v8@@@2@@Z
?GetBackingStore@ArrayBuffer@v8@@QEAA?AV?$shared_ptr@VBackingStore@v8@@@std@@XZ
?GetCurrent@Isolate@v8@@SAPEAV12@XZ
?Global@Context@v8@@QEAA?AV?$Local@VObject@v8@@@2@XZ
?GlobalizeReference@V8@v8@@CAPEA_KPEAVIsolate@internal@2@PEA_K@Z
?HasCaught@TryCatch@v8@@QEBA_NXZ
?Initialize@Locker@v8@@AEAAXPEAVIsolate@2@@Z
?IsArrayBufferView@Value@v8@@QEBA_NXZ
?MoveGlobalReference@V8@v8@@CAXPEAPEA_K0@Z
?New@ArrayBuffer@v8@@SA?AV?$Local@VArrayBuffer@v8@@@2@PEAVIsolate@2@_K@Z
?New@Context@v8@@SA?AV?$Local@VContext@v8@@@2@PEAVIsolate@2@PEAVExtensionConfiguration@2@V?$MaybeLocal@VObjectTemplate@v8@@@2@V?$MaybeLocal@VValue@v8@@@2@UDeserializeInternalFieldsCallback@2@PEAVMicrotaskQueue@2@@Z
?New@External@v8@@SA?AV?$Local@VExternal@v8@@@2@PEAVIsolate@2@PEAX@Z
?New@Function@v8@@SA?AV?$MaybeLocal@VFunction@v8@@@2@V?$Local@VContext@v8@@@2@P6AXAEBV?$FunctionCallbackInfo@VValue@v8@@@2@@ZV?$Local@VValue@v8@@@2@HW4ConstructorBehavior@2@W4SideEffectType@2@@Z
?New@FunctionTemplate@v8@@SA?AV?$Local@VFunctionTemplate@v8@@@2@PEAVIsolate@2@P6AXAEBV?$FunctionCallbackInfo@VValue@v8@@@2@@ZV?$Local@VValue@v8@@@2@V?$Local@VSignature@v8@@@2@HW4ConstructorBehavior@2@W4SideEffectType@2@PEBVCFunction@2@EEE@Z
?New@Isolate@v8@@SAPEAV12@AEBUCreateParams@12@@Z
?New@ObjectTemplate@v8@@SA?AV?$Local@VObjectTemplate@v8@@@2@PEAVIsolate@2@V?$Local@VFunctionTemplate@v8@@@2@@Z
?New@Uint8Array@v8@@SA?AV?$Local@VUint8Array@v8@@@2@V?$Local@VArrayBuffer@v8@@@2@_K1@Z
?NewFromUnsigned@Integer@v8@@SA?AV?$Local@VInteger@v8@@@2@PEAVIsolate@2@I@Z
?NewFromUtf8@String@v8@@SA?AV?$MaybeLocal@VString@v8@@@2@PEAVIsolate@2@PEBDW4NewStringType@2@H@Z
?Parse@JSON@v8@@SA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VString@v8@@@2@@Z
?Reallocate@Allocator@ArrayBuffer@v8@@UEAAPEAXPEAX_K1@Z
?Run@Script@v8@@QEAA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@@Z
?Set@Object@v8@@QEAA?AV?$Maybe@_N@2@V?$Local@VContext@v8@@@2@V?$Local@VValue@v8@@@2@1@Z
?Set@Template@v8@@QEAAXV?$Local@VName@v8@@@2@V?$Local@VData@v8@@@2@W4PropertyAttribute@2@@Z
?SetFatalErrorHandler@Isolate@v8@@QEAAXP6AXPEBD0@Z@Z
?StackTrace@TryCatch@v8@@QEBA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@@Z
?ToLocalEmpty@V8@v8@@CAXXZ
```

### CRYPT32.dll (Import)

```text
CertCloseStore
CertEnumCertificatesInStore
CertFindCertificateInStore
CertFreeCertificateContext
CertGetEnhancedKeyUsage
CertGetIntendedKeyUsage
CertGetNameStringW
CertOpenSystemStoreA
CertOpenSystemStoreW
CryptMsgClose
CryptMsgGetParam
CryptQueryObject
CryptUnprotectData
```

### WS2_32.dll (Import)

```text
WSAAddressToStringW
#116
WSACloseEvent
WSACreateEvent
WSAEnumNetworkEvents
WSAEventSelect
#111
WSAIoctl
WSARecv
WSARecvFrom
WSAResetEvent
WSASend
WSASendTo
#112
WSASocketW
#115
WSAStringToAddressW
WSAWaitForMultipleEvents
#151
#1
#2
#3
#4
freeaddrinfo
getaddrinfo
getnameinfo
#5
#6
#7
#8
#9
#10
#13
#14
#15
#16
#18
#19
#21
#22
#23
```

### SHLWAPI.dll (Import)

```text
StrStrIW
```

### WINMM.dll (Import)

```text
timeGetTime
```

### citizen-resources-client.dll (Import)

```text
??0CachedResourceMounter@fx@@IEAA@PEAVResourceManager@1@@Z
??0RcdBaseStream@resources@@QEAA@PEAVRcdFetcher@1@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
??0RcdStream@resources@@QEAA@PEAVRcdFetcher@1@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
??0ResourceCache@@QEAA@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@0@Z
??0ResourceCacheDeviceV2@resources@@QEAA@AEBV?$shared_ptr@VResourceCache@@@std@@_N@Z
??1CachedResourceMounter@fx@@UEAA@XZ
??1RcdBulkStream@resources@@UEAA@XZ
??1RcdStream@resources@@UEAA@XZ
??1ResourceCache@@QEAA@XZ
??1ResourceCacheDeviceV2@resources@@UEAA@XZ
?AddEntry@ResourceCache@@QEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AEBV?$array@E$0BE@@3@AEBV?$map@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V12@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@U?$pair@$$CBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V12@@std@@@2@@3@@Z
?AddResourceEntry@CachedResourceMounter@fx@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@000_KAEBV?$map@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V12@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@U?$pair@$$CBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V12@@std@@@2@@4@@Z
?AddStatusCallback@CachedResourceMounter@fx@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@AEBV?$function@$$A6AXW4StatusType@CachedResourceMounter@fx@@HH@Z@4@@Z
?Close@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_N_K@Z
?CloseBulk@?$BulkStreamDevice@VRcdStream@resources@@VRcdBulkStream@2@@vfs@@UEAA_N_K@Z
?CloseFile@RcdBulkStream@resources@@MEAAXXZ
?CloseFile@RcdStream@resources@@MEAAXXZ
?Create@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@_N1@Z
?CreateStream@ResourceCacheDeviceV2@resources@@UEAA?AV?$shared_ptr@VRcdStream@resources@@@std@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@4@_N@Z
?EnsureRead@RcdBaseStream@resources@@UEAA_NAEBV?$function@$$A6AX_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z@std@@@Z
?ExistsOnDisk@ResourceCacheDeviceV2@resources@@UEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?ExtensionCtl@ResourceCacheDeviceV2@resources@@UEAA_NHPEAX_K@Z
?FetchEntry@ResourceCacheDeviceV2@resources@@UEAA?AV?$task@URcdFetchResult@resources@@@Concurrency@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?FindClose@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAAX_K@Z
?FindFirst@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEAUFindData@2@@Z
?FindNext@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_N_KPEAUFindData@2@@Z
?Flush@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_N_K@Z
?GetAbsolutePath@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEBA?AV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@XZ
?GetEntryForFileName@ResourceCacheDeviceV2@resources@@UEAA?AV?$optional@V?$reference_wrapper@$$CBUEntry@ResourceCacheEntryList@@@std@@@std@@V?$basic_string_view@DU?$char_traits@D@std@@@4@@Z
?GetHandle@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@QEAAPEAU?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@2@_K@Z
?GetLength@?$BulkStreamDevice@VRcdStream@resources@@VRcdBulkStream@2@@vfs@@UEAA_K_K@Z
?GetRealSize@ResourceCacheDeviceV2@resources@@MEAA_KAEBUEntry@ResourceCacheEntryList@@@Z
?InitializeLoad@CachedResourceMounter@fx@@MEAA?AV?$fwRefContainer@VResource@fx@@@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEAVurl@v1@skyr@@@Z
?IsBlocking@ResourceCacheDeviceV2@resources@@UEAA_NXZ
?LoadResource@CachedResourceMounter@fx@@UEAA?AV?$task@V?$fwRefContainer@VResource@fx@@@@@Concurrency@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?LoadResourceWithError@CachedResourceMounter@fx@@UEAA?AV?$task@V?$expected@V?$fwRefContainer@VResource@fx@@@@VResourceManagerError@fx@@@tl@@@Concurrency@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Open@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@_N1@Z
?OpenBulk@?$BulkStreamDevice@VRcdStream@resources@@VRcdBulkStream@2@@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEA_K@Z
?OpenFile@RcdBulkStream@resources@@MEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?OpenFile@RcdStream@resources@@MEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?PropagateError@ResourceCacheDeviceV2@resources@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Read@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_K_KPEAX0@Z
?Read@RcdStream@resources@@UEAA_KPEAX_K@Z
?ReadBulk@?$BulkStreamDevice@VRcdStream@resources@@VRcdBulkStream@2@@vfs@@UEAA_K_K0PEAX0@Z
?ReadBulk@RcdBulkStream@resources@@UEAA_K_KPEAX0@Z
?RemoveResourceEntries@CachedResourceMounter@fx@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Seek@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_K_K_JH@Z
?Seek@RcdStream@resources@@UEAA_K_JH@Z
?SetPathPrefix@ResourceCacheDeviceV2@resources@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?UnfetchEntry@ResourceCacheDeviceV2@resources@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Write@?$StreamDevice@VRcdStream@resources@@U?$HandleDataWithBulk@VRcdStream@resources@@VRcdBulkStream@2@@detail@vfs@@@vfs@@UEAA_K_KPEBX0@Z
?WriteBulk@?$BulkStreamDevice@VRcdStream@resources@@VRcdBulkStream@2@@vfs@@UEAA_K_K0PEBX0@Z
```

### rage-device-five.dll (Import)

```text
?OnInitialMount@fiDevice@rage@@2V?$fwEvent@$$V@@A
```

### gta-core-five.dll (Import)

```text
?OnInitFunctionEnd@rage@@3V?$fwEvent@W4InitFunctionType@rage@@@@A
?OnInitFunctionStart@rage@@3V?$fwEvent@W4InitFunctionType@rage@@@@A
?OnKillNetworkDone@@3V?$fwEvent@$$V@@A
```

### rage-nutsnbolts-five.dll (Import)

```text
?OnGameFrame@@3V?$fwEvent@$$V@@A
?OnMainGameFrame@@3V?$fwEvent@$$V@@A
```

### net.dll (Import)

```text
?AddReliableHandler@NetLibrary@@QEAAXPEBDAEBV?$function@$$A6AXPEBD_K@Z@std@@_N@Z
?GetGUID@NetLibrary@@QEAA_KXZ
?OnNetLibraryCreate@NetLibrary@@2V?$fwEvent@PEAVNetLibrary@@@@A
```

### legitimacy.dll (Import)

```text
?IDidntDoNothing@@YAXXZ
```

### net-tcp-server.dll (Import)

```text
?GetOrCreate@UvLoopManager@net@@QEAA?AV?$fwRefContainer@VUvLoopHolder@net@@@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
```

### net-base.dll (Import)

```text
??0Buffer@net@@QEAA@XZ
??1Buffer@net@@QEAA@XZ
?GetBuffer@Buffer@net@@QEAAPEAEXZ
?ToString@PeerAddress@net@@QEBA?AV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@XZ
?Write@Buffer@net@@QEAAXPEBX_K@Z
```

### citizen-resources-core.dll (Import)

```text
?GetAllEntries@ResourceMetaDataComponent@fx@@QEAA?AV?$map@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$vector@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@@2@U?$less@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@V?$allocator@U?$pair@$$CBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$vector@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@@2@@std@@@2@@std@@XZ
?GlobEntriesVector@ResourceMetaDataComponent@fx@@QEAA?AV?$vector@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@@std@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@4@@Z
?OnInitializeInstance@Resource@fx@@2V?$fwEvent@PEAVResource@fx@@@@A
?OnInitializeInstance@ResourceManager@fx@@2V?$fwEvent@PEAVResourceManager@fx@@@@A
?TriggerEvent@ResourceEventManagerComponent@fx@@QEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@00PEAVResourceEventComponent@2@@Z
```

### vfs-core.dll (Import)

```text
??0Device@vfs@@QEAA@XZ
??0RagePackfile@vfs@@QEAA@XZ
??0Stream@vfs@@QEAA@V?$fwRefContainer@VDevice@vfs@@@@_K@Z
??1Device@vfs@@UEAA@XZ
?CloseBulk@Device@vfs@@UEAA_N_K@Z
?Create@Device@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@_N1@Z
?CreateDirectoryW@Device@vfs@@UEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?ExtensionCtl@Device@vfs@@UEAA_NHPEAX_K@Z
?GetAttributes@Device@vfs@@UEAAIAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?GetDevice@vfs@@YA?AV?$fwRefContainer@VDevice@vfs@@@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?GetLength@Device@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?GetLength@Stream@vfs@@QEAA_KXZ
?GetModifiedTime@Device@vfs@@UEAA_JAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Mount@vfs@@YAXV?$fwRefContainer@VDevice@vfs@@@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?OpenArchive@RagePackfile@vfs@@QEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEAV34@@Z
?OpenBulk@Device@vfs@@UEAA_KAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@PEA_K@Z
?OpenRead@vfs@@YA?AV?$fwRefContainer@VStream@vfs@@@@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Read@Stream@vfs@@QEAA_KPEAX_K@Z
?ReadBulk@Device@vfs@@UEAA_K_K0PEAX0@Z
?ReadToEnd@Stream@vfs@@QEAA?AV?$vector@EV?$allocator@E@std@@@std@@XZ
?RemoveDirectoryW@Device@vfs@@UEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?RemoveFile@Device@vfs@@UEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?RenameFile@Device@vfs@@UEAA_NAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@0@Z
?Seek@Stream@vfs@@QEAA_K_JH@Z
?SetPathPrefix@Device@vfs@@UEAAXAEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z
?Truncate@Device@vfs@@UEAA_N_K0@Z
?Write@Device@vfs@@UEAA_K_KPEBX0@Z
?Write@Stream@vfs@@QEAA_KPEBX_K@Z
?WriteBulk@Device@vfs@@UEAA_K_K0PEBX0@Z
```

### scripting-gta.dll (Import)

```text
?GetNativeHandlerPtr@ScriptEngine@fx@@SAPEAV?$function@$$A6AXAEAVScriptContext@fx@@@Z@std@@_K@Z
?RegisterNativeHandler@ScriptEngine@fx@@SAX_KV?$function@$$A6AXAEAVScriptContext@fx@@@Z@std@@@Z
```

### rage-scripting-five.dll (Import)

```text
?OnScriptInit@scrEngine@rage@@2V?$fwEvent@$$V@@A
```

### MSVCP140.dll (Import)

```text
??0?$basic_ios@DU?$char_traits@D@std@@@std@@IEAA@XZ
??0?$basic_iostream@DU?$char_traits@D@std@@@std@@QEAA@PEAV?$basic_streambuf@DU?$char_traits@D@std@@@1@@Z
??0?$basic_istream@DU?$char_traits@D@std@@@std@@QEAA@PEAV?$basic_streambuf@DU?$char_traits@D@std@@@1@_N@Z
??0?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAA@PEAV?$basic_streambuf@DU?$char_traits@D@std@@@1@_N@Z
??0?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEAA@XZ
??0_Locinfo@std@@QEAA@HPEBD@Z
??0_Locinfo@std@@QEAA@PEBD@Z
??0_Lockit@std@@QEAA@H@Z
??0facet@locale@std@@IEAA@_K@Z
??0ios_base@std@@IEAA@XZ
??1?$basic_ios@DU?$char_traits@D@std@@@std@@UEAA@XZ
??1?$basic_iostream@DU?$char_traits@D@std@@@std@@UEAA@XZ
??1?$basic_istream@DU?$char_traits@D@std@@@std@@UEAA@XZ
??1?$basic_ostream@DU?$char_traits@D@std@@@std@@UEAA@XZ
??1?$basic_streambuf@DU?$char_traits@D@std@@@std@@UEAA@XZ
??1_Locinfo@std@@QEAA@XZ
??1_Lockit@std@@QEAA@XZ
??1facet@locale@std@@MEAA@XZ
??1ios_base@std@@UEAA@XZ
??4?$_Yarn@D@std@@QEAAAEAV01@PEBD@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@G@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@H@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@I@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@K@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@P6AAEAVios_base@1@AEAV21@@Z@Z
??6?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@_J@Z
??Bid@locale@std@@QEAA_KXZ
??Bios_base@std@@QEBA_NXZ
?_Decref@facet@locale@std@@UEAAPEAV_Facet_base@3@XZ
?_Getcat@?$ctype@D@std@@SA_KPEAPEBVfacet@locale@2@PEBV42@@Z
?_Getcvt@_Locinfo@std@@QEBA?AU_Cvtvec@@XZ
?_Getfalse@_Locinfo@std@@QEBAPEBDXZ
?_Getgloballocale@locale@std@@CAPEAV_Locimp@12@XZ
?_Gettrue@_Locinfo@std@@QEBAPEBDXZ
?_Id_cnt@id@locale@std@@0HA
?_Incref@facet@locale@std@@UEAAXXZ
?_Init@locale@std@@CAPEAV_Locimp@12@_N@Z
?_Ipfx@?$basic_istream@DU?$char_traits@D@std@@@std@@QEAA_N_N@Z
?_Lock@?$basic_streambuf@DU?$char_traits@D@std@@@std@@UEAAXXZ
?_Makeloc@_Locimp@locale@std@@CAPEAV123@AEBV_Locinfo@3@HPEAV123@PEBV23@@Z
?_New_Locimp@_Locimp@locale@std@@CAPEAV123@_N@Z
?_Osfx@?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAXXZ
?_Syserror_map@std@@YAPEBDH@Z
?_Throw_C_error@std@@YAXH@Z
?_Throw_Cpp_error@std@@YAXH@Z
?_Unlock@?$basic_streambuf@DU?$char_traits@D@std@@@std@@UEAAXXZ
?_Winerror_map@std@@YAHH@Z
?_Xbad_alloc@std@@YAXXZ
?_Xbad_function_call@std@@YAXXZ
?_Xinvalid_argument@std@@YAXPEBD@Z
?_Xlength_error@std@@YAXPEBD@Z
?_Xout_of_range@std@@YAXPEBD@Z
?_Xruntime_error@std@@YAXPEBD@Z
?__ExceptionPtrAssign@@YAXPEAXPEBX@Z
?__ExceptionPtrCopy@@YAXPEAXPEBX@Z
?__ExceptionPtrCopyException@@YAXPEAXPEBX1@Z
?__ExceptionPtrCreate@@YAXPEAX@Z
?__ExceptionPtrCurrentException@@YAXPEAX@Z
?__ExceptionPtrDestroy@@YAXPEAX@Z
?__ExceptionPtrRethrow@@YAXPEBX@Z
?__ExceptionPtrToBool@@YA_NPEBX@Z
?c_str@?$_Yarn@D@std@@QEBAPEBDXZ
?classic@locale@std@@SAAEBV12@XZ
?clear@?$basic_ios@DU?$char_traits@D@std@@@std@@QEAAXH_N@Z
?eback@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?egptr@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?epptr@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?fill@?$basic_ios@DU?$char_traits@D@std@@@std@@QEAADD@Z
?flush@?$basic_ostream@DU?$char_traits@D@std@@@std@@QEAAAEAV12@XZ
?good@ios_base@std@@QEBA_NXZ
?gptr@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?id@?$ctype@D@std@@2V0locale@2@A
?id@?$numpunct@D@std@@2V0locale@2@A
?id@?$numpunct@_W@std@@2V0locale@2@A
?imbue@?$basic_ios@DU?$char_traits@D@std@@@std@@QEAA?AVlocale@2@AEBV32@@Z
?imbue@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAAXAEBVlocale@2@@Z
?init@?$basic_ios@DU?$char_traits@D@std@@@std@@IEAAXPEAV?$basic_streambuf@DU?$char_traits@D@std@@@2@_N@Z
?pbase@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?pptr@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEBAPEADXZ
?sbumpc@?$basic_streambuf@DU?$char_traits@D@std@@@std@@QEAAHXZ
?setbuf@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAAPEAV12@PEAD_J@Z
?setf@ios_base@std@@QEAAHHH@Z
?setg@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEAAXPEAD00@Z
?setp@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEAAXPEAD00@Z
?setp@?$basic_streambuf@DU?$char_traits@D@std@@@std@@IEAAXPEAD0@Z
?setw@std@@YA?AU?$_Smanip@_J@1@_J@Z
?sgetc@?$basic_streambuf@DU?$char_traits@D@std@@@std@@QEAAHXZ
?showmanyc@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAA_JXZ
?snextc@?$basic_streambuf@DU?$char_traits@D@std@@@std@@QEAAHXZ
?sputc@?$basic_streambuf@DU?$char_traits@D@std@@@std@@QEAAHD@Z
?sync@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAAHXZ
?tolower@?$ctype@D@std@@QEBADD@Z
?uflow@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAAHXZ
?uncaught_exception@std@@YA_NXZ
?xsgetn@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAA_JPEAD_J@Z
?xsputn@?$basic_streambuf@DU?$char_traits@D@std@@@std@@MEAA_JPEBD_J@Z
_Cnd_broadcast
_Cnd_destroy_in_situ
_Cnd_do_broadcast_at_thread_exit
_Cnd_init_in_situ
_Cnd_wait
_Mbrtowc
_Mtx_destroy_in_situ
_Mtx_init_in_situ
_Mtx_lock
_Mtx_unlock
_Query_perf_counter
_Query_perf_frequency
_Thrd_detach
_Thrd_yield
_Xtime_get_ticks
```

### CONCRT140.dll (Import)

```text
?_Byte_reverse_table@details@Concurrency@@3QBEB
```

### RPCRT4.dll (Import)

```text
RpcStringFreeA
UuidToStringA
```

### WINTRUST.dll (Import)

```text
WinVerifyTrust
```

### CFGMGR32.dll (Import)

```text
CM_Get_Device_Interface_ListW
CM_Get_Device_Interface_List_SizeW
```

### IPHLPAPI.DLL (Import)

```text
GetAdaptersInfo
```

### VCRUNTIME140.dll (Import)

```text
_CxxThrowException
__C_specific_handler
__CxxFrameHandler3
__current_exception
__current_exception_context
__std_exception_copy
__std_exception_destroy
__std_terminate
__std_type_info_compare
__std_type_info_destroy_list
_purecall
memchr
memcmp
memcpy
memmove
memset
strchr
strrchr
strstr
wcschr
wcsrchr
wcsstr
```

### VCRUNTIME140_1.dll (Import)

```text
__CxxFrameHandler4
```

### api-ms-win-crt-stdio-l1-1-0.dll (Import)

```text
__acrt_iob_func
__stdio_common_vfprintf
__stdio_common_vsnprintf_s
__stdio_common_vsprintf
__stdio_common_vsscanf
__stdio_common_vswprintf
_close
_fileno
_lseeki64
_read
_setmode
_wfopen
_wopen
_write
fclose
feof
ferror
fflush
fgetc
fgets
fopen
fputc
fputs
fread
fseek
ftell
fwrite
putchar
setvbuf
```

### api-ms-win-crt-locale-l1-1-0.dll (Import)

```text
___lc_codepage_func
localeconv
```

### api-ms-win-crt-heap-l1-1-0.dll (Import)

```text
_aligned_free
_aligned_malloc
_callnewh
calloc
free
malloc
realloc
```

### api-ms-win-crt-runtime-l1-1-0.dll (Import)

```text
__sys_errlist
__sys_nerr
_beginthreadex
_cexit
_configure_narrow_argv
_crt_atexit
_errno
_execute_onexit_table
_exit
_initialize_narrow_environment
_initialize_onexit_table
_initterm
_initterm_e
_invalid_parameter_noinfo
_invalid_parameter_noinfo_noreturn
_register_onexit_function
_seh_filter_dll
abort
raise
signal
strerror
strerror_s
terminate
```

### api-ms-win-crt-math-l1-1-0.dll (Import)

```text
_dsign
_dtest
_fdsign
_fdtest
_finite
_ldsign
_ldtest
ceilf
floor
ldexp
log
log2
modf
pow
round
```

### api-ms-win-crt-time-l1-1-0.dll (Import)

```text
_gmtime64
_gmtime64_s
_time64
strftime
```

### api-ms-win-crt-string-l1-1-0.dll (Import)

```text
_strdup
_stricmp
_strnicmp
_wcsdup
isalpha
isdigit
isspace
iswspace
strcmp
strcspn
strncat
strncmp
strncpy
strpbrk
strspn
tolower
wcscat_s
wcscpy
wcscpy_s
wcspbrk
```

### api-ms-win-crt-convert-l1-1-0.dll (Import)

```text
_wtoi
atoi
strtod
strtoimax
strtol
strtoll
strtoul
strtoull
wcstombs
```

### api-ms-win-crt-environment-l1-1-0.dll (Import)

```text
getenv
```

### api-ms-win-crt-utility-l1-1-0.dll (Import)

```text
qsort
rand
```

### api-ms-win-crt-filesystem-l1-1-0.dll (Import)

```text
_fstat64
_stat64i32
_unlink
_waccess
_wstat64
_wunlink
```

### bcrypt.dll (Import)

```text
BCryptGenRandom
```

### OLEAUT32.dll (Import)

```text
#200
#201
#2
#6
#7
```

### ole32.dll (DelayImport)

```text
CoCreateFreeThreadedMarshaler
CoInitializeEx
CoTaskMemFree
```

