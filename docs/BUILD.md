# Build and code-change history

This project is **not** a redistributed FiveM fork. It documents local source changes and a separate private CI project that built a targeted component.

## Sources consulted

- Upstream: https://github.com/citizenfx/fivem
- Community proposal: https://github.com/citizenfx/fivem/pull/4050
- Working source branch: https://github.com/Amzi-01/fivem (branch `wine-proton-fix`, when available)
- Existing build repository: `feraskozx1-byte/fivem-pr4050-build` (a separate repository, kept unchanged)

A copy of the original Windows GitHub Actions workflow is preserved at [archive/build-workflow.yml](../archive/build-workflow.yml). The live CI configuration remains in the separate build repository.

## CoreRT targeted experiment

Recorded locally modified files:
- `code/client/citicore/DllGameComponent.Win32.cpp`
- `SEHTableHandler.Win32.cpp`
- `EarlyMode.Win32.cpp`
- `XBRInit.cpp`

They were related to Windows loader/layout and exception-handling compatibility. Do not assume each change was present in the final tested binary; inspect the saved patches and CI provenance.

Successful targeted GitHub Actions run: **42019993897**. The output `CoreRT.dll` was recorded as SHA256 `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64`; preceding copy SHA256 `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013`. These are provenance values, not attached binaries.

## Independent TLS native comparisons

Windows Server 2022 and 2025 controlled fixture CI run: **42379209634**, commit `5d2947dbdf536734d205171804f47d9272aca5e8`, same separate build repository.

The temporary Wine NTDLL API prototype was restricted to an isolated diagnostic environment. The tested original NTDLL hash was `af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5`. A prototype changed the measured return path but did **not** repair the protected library. **Do not deploy it as an Adhesive patch.**

## Source preservation

Recorded end-of-session verification: original Adhesive and installed Proton NTDLL unchanged; code source git status checked; diagnostic `S:` mapping restored; diagnostic prefixes cleaned, and no full runtime patch installed.

See [ARTIFACTS](ARTIFACTS.md) for local source/patch files that can be considered for manual text-only import.
