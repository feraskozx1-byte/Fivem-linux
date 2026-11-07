# Heroic / Epic / Rockstar audit — 2026-11-04

Read-only audit of the existing installation. This report intentionally excludes account identifiers, persona names, authentication arguments, tickets, and tokens.

## Active configuration

- Heroic configuration root: `/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic`.
- GTA Legacy configuration: `GamesConfig/9d2d0eb64d5c44529cece33fe2a46482.json` under that root. The default `config/heroic` copy for this game is empty; using that default would miss the actual configuration.
- Legendary installation metadata: `legendaryConfig/legendary/installed.json`. GTA Legacy reports version `1.0.3889.0_v1`, installation `/home/feras/Games/Heroic/GTAV`, executable `PlayGTAV.exe`.
- Wine prefix: `/home/feras/Games/Heroic/Prefixes/Grand Theft Auto V`.
- **The `pfx` entry within this prefix is a symlink back to the prefix root itself.** Both spellings resolve to the same `drive_c` and registry. Avoid following this self-reference when copying or recursively auditing the prefix.
- Runner path: `/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/tools/proton/Proton-CachyOS-latest/proton`.
- Runner `version` file: `1792530497 cachyos-11.0-20261015-slr`.
- Launch uses UMU, `GAMEID=umu-271590`, and Legendary's Epic integration. The game configuration enables `USE_FAKE_EPIC_EXE=true` and selects `/home/feras/Games/Heroic/GTAV/fix.bat` as its alternative executable.
- Existing `fix.bat` contains `start "" EpicGamesLauncher.exe PlayGTAV.exe %*`. Epic wrapper executables exist in the game directory and `drive_c/windows/command`.

## Epic wrapper is documented compatibility integration

The [official Heroic wiki, Rockstar Games from Epic Games](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Rockstar-Games-from-Epic-Games), edited September 15, 2026 and checked November 4, documents automatic wrapper integration starting with Heroic 2.17, the `USE_FAKE_EPIC_EXE=true` fallback, and the same batch file for older/manual setups. The name of that variable alone is not evidence of forged entitlement. Its purpose here is the documented Epic-to-Rockstar launch integration.

This is separate from PR4050 masking Wine discovery by FiveM protection modules. The documented Heroic wrapper does not establish authorization to conceal Wine from Adhesive or legitimacy components, nor does it establish FiveM secure-server support.

## Evidence from original Rockstar prefix

Source log (sensitive raw file; do not publish wholesale):

`/home/feras/Games/Heroic/Prefixes/Grand Theft Auto V/pfx/drive_c/users/steamuser/Documents/Rockstar Games/Launcher/launcher.log`

| Source line(s) | Sanitized observation |
| --- | --- |
| 63, 65 | Social Club `2.4.0.296`; Rockstar Games Launcher `1.0.110.3139`. |
| 87–88 | Rockstar online configuration downloaded successfully, HTTP 200. |
| 189 | Launcher begins setting up Epic GTA V. |
| 197–198 | Epic metadata read; ownership query initiated for one product. The query alone does not prove its result. |
| 222 | Launcher presence transitions online. |
| 239–244 | GTA5 executable detected with file version `1.0.3889.0`. |
| 287 | Launcher starts the game at 13:13:10 on November 4, 2026. |
| 302–304 | Game exits at 13:14:44 with code 0, interpreted by Rockstar as clean shutdown. |
| 322 | Second game launch at 13:14:50. |
| 344–346 | Second game exit at 13:31:09 with code 0, interpreted as clean shutdown. |

These records demonstrate that the existing original prefix can load Rockstar's online content, process Epic launch integration, and start GTA5. They do **not** prove that gameplay was reached or that any protected server accepted a client. A clean process exit can also follow user cancellation or another early termination path.

Consequently, the isolated `Wine-Test-Prefix` SocialClubHelper/content-loading failures must not be generalized to the original Heroic prefix. Rebuilding or replacing the already functioning original integration is not justified by these records.

## Other checks and distinctions

- `/proc/sys/kernel/yama/ptrace_scope` was read as `1` in this audit. A report describing the failure specifically at value `2` (issue 6046 discussed in the parallel investigation) does not match this machine's current setting. This observation does not rule out every other sandbox or ptrace issue.
- Heroic's log reports GTA V anticheat status denied. The official Heroic wiki discusses GTA Online's BattlEye restriction on Linux separately from working story mode. That is a different product/protection path from FiveM's Adhesive restriction; neither should be used as proof of the other's exact failure mechanism.
- No applications were launched and no original Heroic, GTA, Wine prefix, account, or runner configuration was changed during this audit.
