# Test matrix — observed, not assumed

| Test | Result | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Modified FiveM launcher under Heroic/Proton-CachyOS | **Partial pass** | Client can start under Wine. | Official protection support. |
| Rockstar Launcher and `b3258_GameProc` startup | **Partial pass** | Reached game-process startup stages. | Protected server join. |
| CoreRT targeted build (run 42019993897) | **Pass** | One CI artifact built successfully. | Full FiveM client compatibility. |
| CoreRT change in `Run-CoreRT-Test` | **Partial pass** | The tested client reached `pre-gameload`. | Original Adhesive works. |
| Official `adhesive.dll` load | **Fail** | Error 998, AV at RVA D9FEC5. | Cause of search termination failure. |
| Sticky fallback | **Observed** | Fallback component ran. | Valid secure public-server ticket. |
| Independent TLS/no-TLS fixture | **Pass (29 checks)** | Cross-environment observations reproducible in tested samples. | Relationship to proprietary initializer. |
| TLS return-value prototype | **Pass for targeted API** | 22 pre-fault erroneous returns eliminated in measured run. | Adhesive fix; same AV remained. |
| Missing-name resolver fixture | **Pass (8 checks)** | Test observer can handle an absent exported name. | Adhesive's private target identity. |
| Export bounds metadata comparison | **Pass** | Wine 1468 names, Windows reference 2457 names. | Which export Adhesive needs. |
| Export iterator trace | **Partial pass** | Index increments beyond 1467 to 1477; observed AV. | Initial lookup target or intended stop contract. |
| Protected `ci://` resource support | **Not demonstrated** | — | No protected-resource success proven. |
| Normal `cfxTicket2` / protected public server join | **Fail / not achieved** | Core user goal unresolved. | Whether a future compliant fix is possible. |

## Recorded evidence checkpoints

- `Run-Adhesive-Test/logs/CitizenFX_log_2026-11-04T202008.log`: `Adhesive failed to load under Wine (error 998)`.
- `Run-CoreRT-Test/logs/CitizenFX_log_2026-11-05T124119.log`: `pre-gameload component sticky`.
- `Diagnostics/2026-11-07-TLS-Causality/causality-comparison.json`: controlled before/after conclusions.
- `Diagnostics/2026-11-07-Export-Bounds/FINDINGS.md`: last index-bounds results.

These are paths on the original test machine, **not files asserted to be present in this archive**.
