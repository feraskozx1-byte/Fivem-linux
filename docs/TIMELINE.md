# Research timeline

Dates below follow the available local logs and Codex session exports. The user described the overall effort as approximately **10 days**; detailed recorded development activity is strongest for 2026-11-02 through 2026-11-07.

| Period | Work | Observable result |
| --- | --- | --- |
| Earlier / Nov 2 | Reviewed FiveM-on-Linux community proposals and Wine/Proton constraints; launched GTA V Legacy through Heroic; investigated missing secure authentication ticket. | Windows client assumptions and anti-cheat compatibility were identified as fundamental blockers. |
| Nov 2–3 | Worked with `citizenfx/fivem` PR #4050 and `Amzi-01/fivem` branch `wine-proton-fix`; investigated launcher/WinRT UI paths and Wine environment behavior. | Client source available locally; native loading/launcher compatibility work begun. |
| Nov 4 | Obtained compiled release; tested `FiveM.exe`, `components.json`, loader diagnostics and a Wine test prefix; investigated `CoreRT.dll+0x1B6DF`. | Standalone launcher started, not a supported public-server connection. |
| Nov 4–5 | Targeted changes to `DllGameComponent.Win32.cpp`, `SEHTableHandler.Win32.cpp`, `EarlyMode.Win32.cpp` and `XBRInit.cpp`. Built `CoreRT.dll` through Actions run `42019993897`. | Reached `b3258_GameProc` and `pre-gameload`. `sticky` loaded; `Adhesive` did not. |
| Nov 4–5 | Tested official `adhesive-24769.dll` from the reference directory using isolated diagnostic prefixes; investigated loader error 998 and `0xC0000005` near `D9FEC5`. | Deterministic failure during DLL initialization, original DLL unchanged. |
| Nov 5 | Ghidra/static analysis and debugger observers traced an NTDLL export-name walk and repeated index increment; 1477 iterations noted. | Precise fault path, not the missing API identity or root cause. |
| Nov 7 — TLS | Independent static-TLS/no-TLS fixtures compared Windows Server 2022/2025 with Wine; narrowly changed a public loader return in an isolated prototype. | 29 fixture checks passed; pre-fault nonzero API returns fell from 22 to 0; **same Adhesive crash remained**. |
| Nov 7 — export bounds | Compared NTDLL export-table metadata and observed count/index behavior; validated an independent missing-name resolver test. | Wine `NumberOfNames=1468`, Windows reference `NumberOfNames=2457`. First OOB index 1468, later 1477. No proven generic Wine fix. |
| Nov 7 | Research stopped after repeated tests failed to make protected public servers work. | Archive created, no further claims of a working release. |

See [FINDINGS](FINDINGS.md) and [TEST_MATRIX](TEST_MATRIX.md) for the distinction between evidence and hypotheses.
