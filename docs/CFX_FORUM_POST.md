# Cfx.re Forum post — FiveM/Wine research (ready-to-copy draft)

**Suggested destination:** Reply to the established [Native Linux Support for FiveM — It's Time](https://forum.cfx.re/t/native-linux-support-for-fivem-it-s-time/5330614) topic under *FiveM Discussion → Platform Suggestions*.

**Before posting:** At the latest GitHub check, [feraskozx1-byte/Fivem-linux](https://github.com/feraskozx1-byte/Fivem-linux) is **PUBLIC** and the link can be shared. The original full-history repository has publication risks recorded in [publication audit](PUBLICATION_AUDIT.md); review those concerns. Do not upload proprietary DLLs, private crash dumps, game assets, full Wine prefixes, credentials or tickets.

---

## Title if starting a new topic

**[Linux/Wine Research] 10-day FiveM compatibility investigation — official Adhesive fails at initialization (error 998); asking for upstream guidance**

## Post body

Hello Cfx.re developers and the Linux/FiveM community,

I spent approximately **10 days** researching FiveM **GTA V Legacy** compatibility with Wine/Proton. The primary objective was not just to open the FiveM launcher, but to reach protected public servers with **official, functioning security and legitimate authentication** — without a Windows VM or cloud gaming.

**The project is currently paused and did not achieve that goal.** However, I want to share the research, reproducible public-API fixtures, and failed experiments so someone with deeper knowledge of the client or Wine can help identify the missing compatibility behavior.

### Test environment and provenance

- **Host:** PS5 running Ubuntu Linux using Byepervisor + SonicISO (PS5 firmware 13.60); this is an unusual test platform, so conclusions need independent verification on standard x86-64 Linux.
- **Client:** FiveM for GTA V Legacy, b3258 game-process stage observed, experimental startup derived from community Wine/Proton work around [FiveM PR #4050](https://github.com/citizenfx/fivem/pull/4050).
- **Wine/Proton:** Proton-CachyOS (Wine 11-era), Heroic launcher.
- **Evidence:** Custom C/Python API fixtures, CoreRT-related patches, debugger observers, source analysis and Windows Server 2022/2025 comparisons.

### What worked

1. The experimental client progressed through Rockstar Launcher initialization, `b3258_GameProc`, and `pre-gameload`.
2. A targeted CoreRT compatibility build succeeded, and several independent Wine/Windows public API tests passed.
3. The failure point for the **unmodified official Adhesive** component was localized and repeatedly reproduced.

### Main unresolved issue

When the official `Adhesive 1.0.0.24769` was tested during component initialization under the Wine setup, it failed in `DLL_PROCESS_ATTACH` with:

```text
Adhesive failed to load under Wine (error 998), falling back to sticky.
Exception: 0xC0000005
Faulting module RVA: adhesive+0xD9FEC5
```

A diagnostic run observed a name-table walk against the Wine `ntdll.dll` export directory. In that tested Wine build, `NumberOfNames = 1468`; the observed walk crossed the valid range starting at index 1468 and reached index 1477 at the access violation. A Windows Server 2022 NTDLL reference had 2457 exported names.

**Important limitation:** the export-count difference does *not* establish a root cause. We could not conclusively identify which public API was sought or why that initialization path failed to terminate appropriately.

### What we already ruled out

We separately tested `DisableThreadLibraryCalls` / `LdrDisableThreadCalloutsForDll` with static TLS fixtures on Wine and native Windows Server 2022/2025. A narrow, reversible Wine prototype corrected one observed public API return-value difference, **but the official Adhesive initialization still failed with the same error and crash address**. Therefore that tested difference does not explain this specific failure.

Simply reaching the server browser or falling back to `sticky` is **not a successful workaround**: official protected-resource mounting and normal `cfxTicket2` authentication were not demonstrated to work, and public protected servers remained unavailable.

### What I'm asking Cfx.re and Wine developers

- Is there a **documented/supported compatibility requirement** or public Windows API behavior involved in initializing the original security component under Wine that we have overlooked?
- Can a developer recommend a **non-sensitive diagnostic method or a minimal public-API contract test** that would isolate the Wine compatibility gap without patching or bypassing security checks?
- Is there a roadmap or recommended channel for a future **supported opt-in Linux/Wine compatibility investigation**, or a source-level issue where evidence like this is most useful?

I am **not asking for an anti-cheat bypass, forged tickets, disabling integrity checks, or private implementation details**. I would appreciate any guidance on a legitimate compatibility fix that preserves the original security functionality.

### Full technical archive

- **Research repository:** https://github.com/feraskozx1-byte/Fivem-linux
- **Timeline:** https://github.com/feraskozx1-byte/Fivem-linux/blob/main/docs/TIMELINE.md
- **Findings:** https://github.com/feraskozx1-byte/Fivem-linux/blob/main/docs/FINDINGS.md
- **Tests:** https://github.com/feraskozx1-byte/Fivem-linux/blob/main/docs/TEST_MATRIX.md
- **Original text/source research evidence:** https://github.com/feraskozx1-byte/Fivem-linux/tree/main/local-evidence
- **Main unresolved issue:** https://github.com/feraskozx1-byte/Fivem-linux/issues/1

**Publication note:** The research repository was verified **Public** at the latest check. The published archive includes historical code and experiments; see the repository's third-party attribution and publication audit before distributing copies or attachments.

Thank you for reading. Even if full Linux support is not on the roadmap, a pointer to the correct *public compatibility contract*, official support process, or a reason this cannot be supported would help the community avoid repeating the same investigations.

---

## Checklist before posting

- [ ] **Repository is already Public** at the latest check. Review [publication audit](PUBLICATION_AUDIT.md) and [third-party notices](../THIRD_PARTY_NOTICES.md), especially the historic code and personal paths.
- [ ] Open the GitHub links in a logged-out/private browser window to confirm other people can access them.
- [ ] Do not present the historical patches as a working, supported or anti-cheat-compatible client.
- [ ] Do not upload proprietary `adhesive.dll`, GTA V files, authentication tickets, third-party binaries, raw dumps or personal account details.
- [ ] Reply once to the existing Linux-support topic; **do not cross-post** into support/bug reports.
