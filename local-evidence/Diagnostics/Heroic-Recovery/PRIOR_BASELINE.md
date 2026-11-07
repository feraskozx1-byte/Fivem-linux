# Prior Heroic FiveM baseline

Read-only evidence review on 2026-11-04. No applications were launched, no authentication data was copied, and no existing configuration was changed for this review.

## Original FiveM copy

Location: `/home/feras/Games/Heroic/Prefixes/Grand Theft Auto V/drive_c/FiveM`.

`CitizenFX.ini` specifies `IVPath=S:\Games\Heroic\GTAV` and `DefaultBuild=3258`. `citizen/version.txt` contains `1100010`. This copy contains `legitimacy.dll` and `sticky.dll`; `adhesive.dll` is absent. Successful startup therefore does not establish original protection operating.

Evidence from `logs/CitizenFX_log_2026-11-02T190853.log`:

| Lines | Confirmed event |
|---|---|
| 8 | `InitROS: Epic` |
| 13 | Rockstar Launcher found |
| 16 | `MTL says it's signed in` |
| 342 | `Done running INIT_CORE init functions!` |
| 255–257 | Requesting server variables, obtaining Steam ticket, handshaking with server |
| 258 | `Connection rejected by server: No authentication ticket was specified.` |
| 343–358 | Four further server-variable/handshake attempts end in the same rejection |

The Steam-ticket status text is generic client progress output; it does not establish that Steam is the user's game store or that any authentication ticket was actually issued. The log's `InitROS: Epic` identifies the selected Rockstar launch route.

`logs/CitizenFX_log_2026-11-02T182934.log`, lines 338–14010, records `Updating game storage` progressing from 0% to 100%. This is evidence of game-storage download/patching. It must not be relabeled as server-resource downloads. The user reports previously reaching the server list and downloading server resources, but those specific resource-transfer events have not yet been independently located in this review.

## Existing official-client test

Base: `/home/feras/Games/FiveM-Official-Test`.

`Official-Client-Staging` contains `adhesive.dll` and `sticky.dll`; their presence alone does not establish that either loaded successfully. `Official-Client-Staging/logs/CitizenFX_log_2026-11-03T140631.log`, lines 348–350 and 351–353, records two server-variable/handshake attempts followed by the same missing-authentication-ticket rejection. `Official-Client-Staging/logs/CitizenFX_log_2026-11-03T132741.log`, lines 205–207 and 268–271, records the same outcome.

`Official-Client-Staging/logs/CitizenFX_log_2026-11-03T131744.log`, lines 343–10219, records game-storage updates through 100%; line 10221 switches from build 3258 to build 3889. Other newer logs stop at Rockstar connection error 506, so earlier successful startup must not be replaced with an assumption that Rockstar never worked.

## Heroic launch entry and runner

Heroic profile: `/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic`.

- Sideload library: `sideload_apps/library.json`.
- Entry ID: `wC6nr6dqw6GVLd8H6ysDhV`; title: `FiveM Official Test`.
- Game settings: `GamesConfig/wC6nr6dqw6GVLd8H6ysDhV.json`.
- Registered executable: `/home/feras/Games/FiveM-Official-Test/installer/FiveM.exe`.
- Configured prefix: `/home/feras/Games/FiveM-Official-Test/GTA-Prefix-Work`.
- Configured runner: `Proton-CachyOS-latest`, executable in the profile's `tools/proton/Proton-CachyOS-latest/proton`.
- GameMode, esync, fsync, automatic DXVK and VKD3D are enabled; environment and wrapper option arrays are empty in this sideload entry.

The existing `/home/feras/Games/FiveM-Official-Test/run-official.sh` reconstructs a separate diagnostic launch through Flatpak and UMU:

```text
flatpak run --command=sh com.heroicgameslauncher.hgl
  WINEPREFIX=/home/feras/Games/FiveM-Official-Test/GTA-Prefix-Work
  PROTONPATH=<config-epic2 Heroic profile>/tools/proton/Proton-CachyOS-latest
  GAMEID=umu-default
  CitizenFX_NoTenUI=1
  <profile>/tools/runtimes/umu/umu_run.py
    /home/feras/Games/FiveM-Official-Test/Official-Portable/FiveM.exe
```

This is a launch recipe found on disk, not a launch newly performed during this review. It differs materially from invoking an EXE with system Wine.

Prior protocol investigation also exists at `diagnostics-20261103/auth-followup/ACCOUNT-PROTOCOL-TRACE.md`. Its existence is noted to avoid repeating earlier work; its contents were not audited for this baseline.

## What this establishes

The user's previous progress is corroborated beyond opening Rockstar: FiveM initialized the game and exchanged a server handshake. The concrete observed failure is missing connection authentication, not merely failure to locate Launcher. These historical logs do not establish successful secure-server acceptance, a currently reproducible launch, or a solution to the protection restriction.
