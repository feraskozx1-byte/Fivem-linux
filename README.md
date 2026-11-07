# FiveM on Linux — PS5 / Wine Compatibility Research (Archived)

> **Status: PAUSED — NO WORKING PUBLIC-SERVER SUPPORT.**  
> This repository documents an approximately ten-day independent investigation into running the FiveM GTA V Legacy client on Linux. It is an engineering archive and **not** a working FiveM Linux distribution, anti-cheat workaround, or verified solution to public-server authentication.

[العربية](README.ar.md) · [Timeline](docs/TIMELINE.md) · [Technical findings](docs/FINDINGS.md) · [Test matrix](docs/TEST_MATRIX.md) · [Unresolved blockers](docs/BLOCKERS.md) · [Artifact inventory](docs/ARTIFACTS.md) · [Safe evidence import](docs/IMPORT.md)

## Mission

Run the FiveM client natively under Wine/Proton on Linux (not a Windows VM, not cloud gaming) and connect to protected public servers using the original, unmodified authentication/protection components. The test host was a PlayStation 5 with Ubuntu booted by Byepervisor + SonicISO on firmware 13.60. The extremely slow external USB HDD made rebuilding and duplicating gigabytes costly.

## What was achieved

- Investigated and built from the community Wine/Proton compatibility proposal [citizenfx/fivem PR #4050](https://github.com/citizenfx/fivem/pull/4050) / `Amzi-01/fivem` `wine-proton-fix`.
- Tracked a `CoreRT.dll` crash (`+0x1B6DF`) and tested targeted source changes affecting startup, exception-handling and Windows-layout assumptions. A targeted `CoreRT.dll` CI build succeeded (GitHub Actions run `42019993897` in the separate build repository).
- The modified FiveM client reached Rockstar Launcher initialization, `b3258_GameProc`, `pre-gameload`, and the connection stage. This **was not** proof that official Adhesive had initialized.
- Reproduced official `adhesive.dll` loader failure: `ERROR_NOACCESS (998)`, with `0xC0000005` during initialization at `adhesive+0xD9FEC5`. The test client fell back to `sticky`.
- Developed isolated Wine API/PE loader test fixtures, debugger observers and native Windows/Wine comparisons. The `DisableThreadLibraryCalls` / static-TLS return difference was reproducible; a narrow Wine prototype corrected the return values but **did not fix Adhesive**.
- Traced the failing NTDLL export-name iteration: `NumberOfNames=1468` under the tested Wine build, first out-of-range index `1468`, later observed index `1477`, invalid name-RVA read `0x130012`. **The identity of the lookup target and the reason for lacking an effective bound remain unknown.**

## What did NOT work

Official Adhesive initialization, protected `ci://` resource support, the normal `cfxTicket2` authentication path, and public protected servers were **not** demonstrated working. Disabling an insecure-mode warning, using Sticky, or merely reaching the server browser is not a solution.

**No protection bypass or fabricated ticket is provided here.** Official protection binaries, credentials, account data, private crash dumps, and GTA V assets are deliberately not redistributed.

## Repository layout

- `README.ar.md` — Arabic project overview
- `docs/TIMELINE.md` — chronological experiments
- `docs/FINDINGS.md` — evidence-based analysis of the last blockers
- `docs/TEST_MATRIX.md` — what passed, failed, and remains untested
- `docs/BLOCKERS.md` — unresolved questions, limitations and next legitimate paths
- `docs/BUILD.md` — provenance of the separate targeted build
- `docs/ARTIFACTS.md` — original local artifact locations and privacy restrictions
- `docs/IMPORT.md` + `scripts/import-local-evidence.sh` — optional, conservative method to add **selected** text/code/patch files from the PS5 filesystem. They are **not yet imported** merely by this documentation commit.

## Research provenance and caveats

The summary is reconstructed from shared Codex session exports and their recorded terminal output, not by directly accessing the original PS5 filesystem. Trace conclusions are **observations** from the tested versions; they should not be generalized to all FiveM/Adhesive/Wine releases. Source code and binaries not attached to this conversation remain on the original PS5 disk until explicitly imported. See [ARTIFACTS](docs/ARTIFACTS.md).

## Attribution

FiveM and its original protection components belong to their respective rights holders. Wine/Proton and community PR authors retain their respective licenses. This archive documents testing and links to upstream code; it does not claim ownership of upstream sources or grant a license to private third-party binaries.

*Research paused 2026-11-07.*