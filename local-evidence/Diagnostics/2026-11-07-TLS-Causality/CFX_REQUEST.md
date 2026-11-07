# Adhesive 1.0.0.24769: static-TLS return difference ruled out for this failure

Local draft only; not submitted. No private DLL, memory dump, account data, or authentication material is attached.

Official Adhesive SHA256: `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`.
Wine11.0 / Proton-CachyOS on Linux x64. Offline real-client initialization in a separate diagnostic prefix fails in DLL_PROCESS_ATTACH with access violation at RVA`D9FEC5`, followed by loader error998.

New controlled exclusion: our independent static-TLS fixture and no-TLS control pass29checks natively on Windows Server2022/build20348 and Server2025/build26100. The exact downloaded PE binaries also pass all29checks on Wine, with identical TLS data and notification observations. Native `LdrDisableThreadCalloutsForDll(static TLS DLL)` returns success and Win32 returns TRUE, retaining TLS notifications; Wine returns C0000135/FALSE. A public-loader-only correction returns success without suppressing TLS notifications and matches both native fixtures.

In the real client, the correction removes all22nonzero returns among77pre-fault calls, with identical module/caller ordering, but leaves the same fault and index-production sequence. All78observed calls including one post-fault call return success. Neither Adhesive as the module argument nor a direct caller inside Adhesive is observed before the fault. Debugger instrumentation never overrides application registers or results. Only the ordinary public Wine loader implementation changes; the official DLL remains byte-identical. This excludes that return-status difference as the cause of this observed failure.

The iterator starts at0 and reaches1477 with NumberOfNames1468. New producer tracing at RVA`DA4EE8` observes `ESI = R13 + 1`1477times; R13 equals the previous saved index at stack+0x40, and the next consumer at`D9FDD5` uses exactly that value+1. First out-of-range index is1468. At1477, the name-RVA read accesses the adjacent ordinal words18/19, producing0x130012, followed by the invalid byte read at`D9FEC5`. Thus1477 is accumulated iteration, not an initial Windows ordinal/hint. Earlier probes observed no successful comparison for valid entries; no internal comparison or security decision was altered.

**Specific missing information requested:** identify the public NTDLL export sought by this initializer and the intended no-match/termination contract at the transition1467→1468. A vendor diagnostic build that logs the requested public API name and the bound used before incrementing the iterator is sufficient; no anti-cheat algorithm or unrestricted private symbols are requested.

That information will distinguish a genuinely missing Windows API implementation suitable for Wine development from an initializer assumption requiring a Cfx.re change. Padding/reordering exports, changing comparisons, and swallowing access violations have not been used. We do not claim that successful loading alone would validate all protection functions.

Public independent native test provenance: [CI42379209634](https://github.com/feraskozx1-byte/fivem-pr4050-build/actions/runs/42379209634), commit`5d2947dbdf536734d205171804f47d9272aca5e8`. No Adhesive binary or private client trace was uploaded there.
