# Original diagnostic and source evidence / ملفات التجارب الأصلية

[Main page](../README.md) · [العربية](../README.ar.md) · [Experiment index](../docs/EXPERIMENTS.md)

This folder holds **179 text/source files imported from the original PS5 Ubuntu workspace** in commit `58cd24c` (2026-11-07; 18,011 lines added). They are historical evidence, **not a working application**.

- [Diagnostics/](Diagnostics/) — independent compatibility tests, Markdown notes, source-code probes, experimental patches and fixtures.
- [PR-4050.patch](PR-4050.patch) — captured upstream proposal patch.
- [local-source-working-tree.patch](local-source-working-tree.patch) — staged snapshot of local source working-tree differences.
- [local-source-index.patch](local-source-index.patch) — staged snapshot of local source Git index differences.

## Where to start

1. [Final export-bounds research](Diagnostics/2026-11-07-Export-Bounds/FINDINGS.md)
2. [TLS causality results](Diagnostics/2026-11-07-TLS-Causality/FINDINGS.md)
3. [Compatibility experiments](Diagnostics/2026-11-05-Compatibility/REPORT_AR.md)
4. [CoreRT and loader work](Diagnostics/2026-11-04/RESULTS_AR.md)

More links and explanations: [docs/EXPERIMENTS.md](../docs/EXPERIMENTS.md).

## Do not infer success from a filename

Names like `Direct-Repair`, `Compatibility-Fix` or `PATCH.md` refer to experimental stages. Their existence **does not mean** Adhesive was fixed or servers became playable.

The original client binaries, Wine prefixes, official Adhesive DLL, GTA V files, private crash dumps and credentials are **not** included. See [ARTIFACTS](../docs/ARTIFACTS.md) for provenance and exclusions.
