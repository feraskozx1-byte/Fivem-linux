# FiveM PR #4050 source audit — 2026-11-04

Scope: static inspection of the existing checkout at commit `ba07d9d3d5bd8459b69a81c69eb6065d4e11273c`, the saved PR patch, and existing release files. This audit makes no claim of runtime testing, successful authentication, or a server connection. Existing source and workflows were not modified.

## Secure-server objective

The existing PR build is insufficient evidence that original authentication and protection operate in a supported configuration:

1. [WineCompat.Win32.cpp, lines 34–45 and 67–79](../../Original-PR4050-Source/code/client/citicore/WineCompat.Win32.cpp#L34) hooks Windows `GetProcAddress` and returns null for Wine identity exports. Its comments expressly identify `legitimacy.dll` and `adhesive.dll` as intended affected callers. [EarlyMode.Win32.cpp, lines 16–19](../../Original-PR4050-Source/code/client/citicore/EarlyMode.Win32.cpp#L16) installs the hook before these components load. This changes environment detection in authentication/protection components; it is not merely an implementation of a missing Windows API.
2. [ComponentLoader.cpp, lines 175–193](../../Original-PR4050-Source/code/client/citicore/ComponentLoader.cpp#L175) removes the upstream Wine-forced insecure path. Removing its warning does not demonstrate that protection works.
3. [DllGameComponent.Win32.cpp, lines 134–148](../../Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp#L134) falls back from failed Adhesive loading to `sticky.dll`; its own comment describes reduced security. The existing manifest fallback at lines 203–207 also substitutes Sticky when the Adhesive manifest cannot load.
4. `adhesive.dll` is absent from both existing `Run-Test` and `Compiled-Release` trees, while `sticky.dll` is present and `components.json` requests Adhesive. A menu or launcher opened with this layout cannot establish that Adhesive loaded.

Upstream evidence is decisive for the **supported** objective: [radium-cfx's October 15, 2026 review comment](https://github.com/citizenfx/fivem/pull/4050#discussion_r4289067271) states that Cfx does not currently intend to permit Linux clients to connect to secure game servers and therefore cannot merge these changes. This establishes an upstream support restriction, not experimental proof that every possible Wine execution fails at a particular network packet. No server rejection was reproduced in this static audit.

The user's required supported secure path consequently needs Cfx cooperation and validation of the original protection stack. Hiding Wine detection or substituting Sticky would not satisfy that requirement. Legitimate Rockstar/Epic compatibility diagnosis can continue independently.

## CoreRT crash and the two proposed remedies

[DllGameComponent.Win32.cpp, lines 36–46](../../Original-PR4050-Source/code/client/citicore/DllGameComponent.Win32.cpp#L36) reads the PEB OS build number and, for `18362 <= build < 19628`, accesses `_fltused - 16` inside `ntdll`. This assumes an undocumented Windows memory layout. The saved handoff maps the existing `CoreRT.dll+0x1B6DF` write fault to line 46. That mapping is prior evidence, not a new runtime reproduction here.

Adding `&& !CfxIsWine()` to this condition directly excludes the Windows layout assumption on Wine, independently of reported Windows version. The destructor at lines 69–72 restores the old value only when its optional was populated, so skipping the constructor block also skips the corresponding write on destruction. The local source still contains the original condition. The handoff records the fix in workflow commit `f4ee8bf856e40373cf0d7fd7b06ee7c4e24099ca`, without a rebuilt local DLL.

Reporting Windows build 22000 also excludes this exact branch. It is a useful temporary control provided the actual process receives that version; a per-application registry override or a different runner/prefix can change the result. The source guard is the more targeted durable remedy. Neither remedy validates authentication or protection.

## Smallest reasonable Windows build

[client/citicore/premake5.lua, lines 1–4](../../Original-PR4050-Source/code/client/citicore/premake5.lua#L1) defines project `CitiCore`, output `CoreRT.dll`. Its declared dependencies at lines 22–28 include `Shared`, Boost program options/locale, TBB, MinHook, and udis86. After normal matching-source setup, dependency preparation, solution generation, and restore on Windows/VS 2022, the scoped target is:

```powershell
msbuild code\build\five\CitizenMP.sln /t:CitiCore /p:Configuration=Release /p:Platform=x64 /m
```

This command is a proposed build invocation, not one executed or verified here. It builds the target's dependency graph instead of the entire client. [tools/fxd/build.ps1, lines 16–32](../../Original-PR4050-Source/code/tools/fxd/build.ps1#L16) identifies the solution path and standard MSBuild configuration.

The saved release artifact is not an incremental build cache: no object files/generated solution are present locally, and `Compiled-Release` lacks `Shared.lib` and `CoreRT.lib`. Reusing the existing runtime layout is reasonable, but directly relinking the changed object from these release files is not currently available. A fresh scoped build would still need required dependencies; its actual duration has not been measured. It would also retain this PR's environment-hiding changes unless those were deliberately removed in a separate reviewed source variant.

The official release pipeline additionally requires private tooling for public client releases: [cfxRunMSBuild.psm1, lines 15–19](../../Original-PR4050-Source/code/tools/ci/psm1/cfxRunMSBuild.psm1#L15). A locally successful source build is therefore distinct from an officially supported production release.
