# Documentation hub / فهرس التوثيق

**Status:** research paused 2026-11-07 · **No working protected public-server implementation**.

[Home](../README.md) · [العربية](../README.ar.md) · [Raw evidence](../local-evidence/README.md)

## Read the project in order

| # | Document | Purpose |
| :-: | :-- | :-- |
| 1 | [README (English)](../README.md) / [الملخص بالعربية](../README.ar.md) | Goals, achievements, limitations and result |
| 2 | [Timeline](TIMELINE.md) | Chronology of the ~10-day investigation |
| 3 | [Experiments and file map](EXPERIMENTS.md) | Where each test's original artifacts live |
| 4 | [Test matrix](TEST_MATRIX.md) | Controlled tests, observed results and their limits |
| 5 | [Technical findings](FINDINGS.md) | CoreRT, Adhesive 998, export bounds, TLS comparison |
| 6 | [Final blockers](BLOCKERS.md) | Why the outcome remained unachieved |
| 7 | [Build history](BUILD.md) | PR #4050-related changes and independent CI |
| 8 | [Artifact inventory](ARTIFACTS.md) | What was uploaded and what was withheld |
| 9 | [FAQ](FAQ.md) | Clarifies interpretation and common questions |
| 10 | [Privacy policy](PRIVACY.md) | Sensitive and proprietary material exclusions |
| 11 | [Evidence import](IMPORT.md) | How the reviewed text-only evidence was archived |
| 12 | [Credits](SOURCE_AND_CREDITS.md) | Upstream authors, references, licenses |
| 13 | [About suggestions](REPOSITORY_ABOUT.md) | Suggested sidebar description and topics |

## Evidence directory

The repository includes [179 imported files](../local-evidence/README.md) in the 2026-11-07 text/source import commit. They include human-written reports, patches, fixtures, Python analyses and diagnostic probes—not the complete binary runtime. The exact test environment was on the original PS5 Ubuntu drive; this repository does not provide a turnkey local reproducer.

- [CoreRT compatibility](../local-evidence/Diagnostics/2026-11-05-Compatibility/)
- [Ghidra research](../local-evidence/Diagnostics/2026-11-05-Adhesive-Ghidra/)
- [Adhesive RCA](../local-evidence/Diagnostics/2026-11-05-Adhesive-RCA/)
- [TLS causality](../local-evidence/Diagnostics/2026-11-07-TLS-Causality/)
- [Export bounds](../local-evidence/Diagnostics/2026-11-07-Export-Bounds/)

## Source vs. inference

An **observed result** appears in a saved log, script output or report. An **investigative hypothesis** is a potential explanation not established by the tests. The pages deliberately retain that separation. A crash address or differing export count is not itself a general Wine bug or a successful compatibility patch.

## Project status

The central [GitHub issue #1](https://github.com/feraskozx1-byte/Fivem-linux/issues/1) records the unsolved initialization fault. The project is paused. The issue is retained for research history—not as a claim that someone is actively maintaining a working fix.
