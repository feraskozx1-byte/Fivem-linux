# Experiment index — original evidence

[Home](../README.md) · [Documentation hub](INDEX.md) · [Test matrix](TEST_MATRIX.md)

This directory maps imported text/code artifacts to the **question being investigated**. Folder names reflect the original Codex experiment sessions; many include superseded attempts, not verified fixes. Do not execute a random script or patch against your live Wine installation.

| Date / track | Evidence directory | Focus / outcome |
| :-- | :-- | :-- |
| Nov 4 | [CoreRT/heroic baseline](../local-evidence/Diagnostics/2026-11-04/) | Startup layout assumption and initial environment audit |
| Nov 5 | [Compatibility](../local-evidence/Diagnostics/2026-11-05-Compatibility/) | Source patches, loader/SEH probes, CoreRT CI preparation |
| Nov 5 | [Compatibility fix](../local-evidence/Diagnostics/2026-11-05-Compatibility-Fix/) | Hypotheses, contract fixtures and test results |
| Nov 5 | [TLS compatibility](../local-evidence/Diagnostics/2026-11-05-TLS-Compatibility/) | Static TLS test harness |
| Nov 5 | [Adhesive investigation](../local-evidence/Diagnostics/2026-11-05-Adhesive-Investigation/) | First loader-init diagnostics and native comparisons |
| Nov 5 | [Adhesive phase 2](../local-evidence/Diagnostics/2026-11-05-Adhesive-Phase2/) | Standalone initialization checks |
| Nov 5 | [Direct-repair study](../local-evidence/Diagnostics/2026-11-05-Adhesive-Direct-Repair/) | Experimental startup/diagnostic patches; **not a confirmed repair** |
| Nov 5 | [Ghidra](../local-evidence/Diagnostics/2026-11-05-Adhesive-Ghidra/) | Static observations and public import audit |
| Nov 5 | [Index trace](../local-evidence/Diagnostics/2026-11-05-Adhesive-Index-Trace/) | Index sequence and independent fixtures |
| Nov 5 | [Loop limit](../local-evidence/Diagnostics/2026-11-05-Adhesive-Loop-Limit/) | Export iterator instrumentation |
| Nov 5 | [Resolver probe](../local-evidence/Diagnostics/2026-11-05-Adhesive-Resolver-Probe/) | Resolver comparison, missing/known-name exercises |
| Nov 5 | [Root cause analysis](../local-evidence/Diagnostics/2026-11-05-Adhesive-RCA/) | Index provenance and unresolved target |
| Nov 7 | [TLS causality](../local-evidence/Diagnostics/2026-11-07-TLS-Causality/) | Controlled return-value prototype **failed to resolve the crash** |
| Nov 7 | [Export bounds](../local-evidence/Diagnostics/2026-11-07-Export-Bounds/) | End-of-project NTDLL export-name and watchpoint findings |
| Various | [Heroic recovery](../local-evidence/Diagnostics/Heroic-Recovery/) | Prior configuration baseline and startup notes |

## Evidence packages worth reading

| Artifact | Description |
| :-- | :-- |
| [`2026-11-07-Export-Bounds/FINDINGS.md`](../local-evidence/Diagnostics/2026-11-07-Export-Bounds/FINDINGS.md) | Most recent observed export-boundary behavior |
| [`2026-11-07-TLS-Causality/FINDINGS.md`](../local-evidence/Diagnostics/2026-11-07-TLS-Causality/FINDINGS.md) | Controlled experiment showing TLS patch was **not causal** |
| [`2026-11-05-Adhesive-RCA/REPORT_AR.md`](../local-evidence/Diagnostics/2026-11-05-Adhesive-RCA/REPORT_AR.md) | Arabic account of the internal fault investigation |
| [`2026-11-05-Compatibility/REPORT_AR.md`](../local-evidence/Diagnostics/2026-11-05-Compatibility/REPORT_AR.md) | Earlier startup compatibility notes |
| [`PR-4050.patch`](../local-evidence/PR-4050.patch) | Historical PR patch copy; upstream retains ownership |
| [`local-source-working-tree.patch`](../local-evidence/local-source-working-tree.patch) | Captured working-tree diff (may be empty if work was already committed) |
| [`local-source-index.patch`](../local-evidence/local-source-index.patch) | Captured staged diff (may be empty) |

## Important context

- These are **research artifacts, not a runnable distribution**.
- Some code is observation tooling that assumes proprietary test binaries and a specific local prefix, deliberately not uploaded.
- The README and test matrix describe what is known, not everything the historical code attempted.
- No credentials, client tickets, original protection DLLs or game binaries are hosted here.

[Read the final blocker →](BLOCKERS.md)
