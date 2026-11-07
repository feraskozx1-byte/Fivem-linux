# Technical findings and evidence

This report summarizes observations from Codex's recorded local commands and final research notes. It is **not** an independent reproduction on a fresh machine. Values are specific to the tested binary and Wine version.

## 1. FiveM launcher and CoreRT

The PR #4050-derived modified FiveM build started under a Proton-CachyOS Wine runtime within the Heroic setup. The earlier `CoreRT.dll+0x1B6DF` fault led to targeted source compatibility changes and a successful targeted CoreRT build. A later log showed `b3258_GameProc` entering `pre-gameload`, including `pre-gameload component sticky`. This is client progress, but **not evidence of Adhesive initialization or protected public-server authentication**.

## 2. Original Adhesive loader failure

Test version: `Adhesive 1.0.0.24769`, recorded official SHA256:

`3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`

Recorded FiveM line:

```text
Adhesive failed to load under Wine (error 998), falling back to sticky.
```

Error 998 is `ERROR_NOACCESS`. Independent tests reported exception `0xC0000005` during `DLL_PROCESS_ATTACH`, at relative virtual address `adhesive+0xD9FEC5`. The initialization stage was associated with `UCRT _initterm`.

The crash's observed final instruction does **not** identify the first fault in the application logic. It is not evidence that a particular protected check should be removed.

## 3. The export-name walk

The analyzed Wine NTDLL PE export directory had `NumberOfNames = 1468` (and 1468 function slots). The reported native reference, Windows Server 2022 NTDLL 10.0.20348.5622, had `NumberOfNames = 2457` (2458 function slots). Different export counts **do not**, on their own, demonstrate a missing API required by Adhesive.

At the first lookup the observed NTDLL name count was 1468, and it remained 1468 at the fault. Tracing showed the candidate index being formed as `previous + 1`; first out-of-bounds value was 1468 and the fault was observed at 1477. The latter read a 32-bit quantity `0x130012` from data extending into the adjacent ordinals table and used it as an invalid name RVA before the `D9FEC5` fault.

The export name table immediately precedes the ordinal table **on both Wine and the Windows reference**; there is no `NULL` name sentinel contract at the end of the table.

An observer recorded 71 pre-AV interface-level pairs and no resolver events during this export walk that revealed the desired name. A read/write watch remained enabled for the count field; no further access on the observed initialization thread was recorded during the walk. This **does not prove** that the bound was never read or cached earlier, or that the needed API is definitely absent.

**Unresolved:** the intended lookup target and effective termination/bounds condition when moving from index 1467 to 1468.

## 4. Static TLS and DisableThreadLibraryCalls

An independent small PE with static TLS and a no-TLS control was tested on native Windows Server 2022 and 2025 and Wine; 29 recorded checks passed with the same binary samples. A public loader API return-value difference was found for a static TLS DLL: native Windows returned success while the tested Wine path returned failure.

Codex created an isolated, reversible source-backed *binary prototype* (not a full Wine source rebuild). It changed public API results as predicted and preserved thread callbacks. In the FiveM diagnostic scenario, **22 of 77 pre-fault nonzero callout status values became 0**, while `D9FEC5`, the index sequence and error 998 remained. Therefore **that particular TLS return difference was causally excluded as the cause of this observed Adhesive failure**. Other potential TLS defects were not exhaustively excluded.

**Do not install that TLS prototype as an Adhesive fix.** The original Proton installation was not modified.

## 5. Exclusions and limitations

- Cannot infer authentication success from reaching `pre-gameload` or the server browser.
- Cannot infer protection works from replacing `sticky` with any nonofficial module.
- No tested patch fixed original Adhesive initialization.
- No evidence demonstrates a missing *specific* NTDLL API as the crash's cause.
- Adding padding, changing export ordering, swallowing the access violation or bypassing protection would not constitute a verified compatibility fix.
- Windows reference and Wine observations arose from specific versions; exports are not stable across all builds.

See [BLOCKERS](BLOCKERS.md) and the original local `Diagnostics/2026-11-07-Export-Bounds/FINDINGS.md` (to be imported separately).
