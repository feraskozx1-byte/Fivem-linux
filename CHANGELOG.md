# Changelog — archived milestones

This is a **research history**, not software release history. No working FiveM Linux version was released.

## 2026-11-07 — Research paused / archive saved

- Recorded the last NTDLL export-name boundary investigation.
- Confirmed that the isolated public-loader TLS return-value prototype **did not** fix the Adhesive initialization failure.
- Preserved the known error `998` / `0xC0000005` and unresolved public-server authentication path.
- Archived project notes, CI workflow, source patches, fixtures and diagnostic reports.
- Imported 179 text/source evidence files from the PS5 Ubuntu workspace.

## 2026-11-05 — Launcher/CoreRT/Adhesive research

- Worked through Wine/Proton launcher and CoreRT compatibility changes.
- Achieved partial client startup and game preloading stages.
- Recorded original Adhesive crash and investigative probes, including export-iterator tracing.
- No valid protected public-server join.

## 2026-11-02 to 2026-11-04 — Early client compatibility and build

- Evaluated FiveM-on-Linux proposals and PR #4050-derived client.
- Built and tested client components against Heroic and Wine/Proton.
- Reproduced launcher and CoreRT failures, and started isolated diagnostics.

See [timeline](docs/TIMELINE.md) and [technical results](docs/FINDINGS.md). Dates reflect available test logs, not necessarily every experiment.
