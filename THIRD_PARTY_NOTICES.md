# Third-party copyright and license notices

This repository is a **mixed-license research archive**. It is not a single MIT/GPL-licensed project. Copied source retains the rights of its original authors. Making this repository public would not relicense any third-party materials.

## CitizenFX / FiveM — LGPL 2.0 exception for listed directories

The official [FiveM LICENSE](https://github.com/citizenfx/fivem/blob/master/LICENSE) covers many source components under Rockstar/Cfx.re terms, but explicitly lists `code/client/citicore/`, `code/client/launcher/`, `code/client/shared/` and certain other directories as GNU Library GPL **version 2** (LGPL-2.0-only). Third-party components may have separate terms. The archived `DllGameComponent.Win32.cpp` and relevant `PR-4050.patch` hunks refer to these listed directories.

- Full license: [LICENSES/LGPL-2.0-only.txt](LICENSES/LGPL-2.0-only.txt).
- Source: [citizenfx/fivem](https://github.com/citizenfx/fivem) and [original license](https://github.com/citizenfx/fivem/blob/master/LICENSE).
- Third-party credits: [upstream THIRD_PARTY_NOTICES](https://github.com/citizenfx/fivem/blob/master/THIRD_PARTY_NOTICES.md).
- Community source patch: [upstream PR #4050](https://github.com/citizenfx/fivem/pull/4050) / [Amzi-01/fivem](https://github.com/Amzi-01/fivem/tree/wine-proton-fix). The `From:` author attribution is preserved in [PR-4050.patch](local-evidence/PR-4050.patch).

**Caution:** some historical patch experiments affect how the client handles Wine/protection-related detection. This notice does not certify their compliance with game-service terms or legality of redistribution in every jurisdiction.

## Wine — LGPL 2.1 or later

The archived [`dlls/ntdll/loader.c` source](local-evidence/Diagnostics/2026-11-07-TLS-Causality/public-source/dlls/ntdll/loader.c) is copied Wine code under GNU Lesser GPL **version 2.1 or later**, according to its file header. Original notices: **Copyright 1995, 2003 Alexandre Julliard** and **Copyright 2002 Dmitry Timoshkov for CodeWeavers**.

- Full text: [LICENSES/LGPL-2.1.txt](LICENSES/LGPL-2.1.txt).
- Upstream: [wine-mirror/wine](https://github.com/wine-mirror/wine) and [COPYING.LIB](https://github.com/wine-mirror/wine/blob/master/COPYING.LIB).

## MinHook — source-header redistribution license

The archived [`MinHook.h`](local-evidence/Diagnostics/2026-11-05-Compatibility/build-validation/pinned/MinHook.h) retains the original header: **Copyright (C) 2009–2017 Tsuda Kageyu**, including source redistribution conditions and warranty disclaimer.

- Full text: [LICENSES/MinHook-LICENSE.txt](LICENSES/MinHook-LICENSE.txt).
- Upstream: [TsudaKageyu/minhook](https://github.com/TsudaKageyu/minhook/blob/master/LICENSE.txt).

## Remaining files, documentation and scope

Other scripts, traces, diffs and reports may contain original user-authored material plus third-party excerpts. No repository-wide redistribution license for *all* such materials has been chosen by the owner. Refer to individual file notices and upstream license files before reusing.

The archived repository does not redistribute official Adhesive binaries, GTA V game assets, session credentials or complete compiled clients.

This attribution file is **not a complete legal audit, license warranty or proof of permission for every historical commit**. Read [PUBLICATION_AUDIT.md](docs/PUBLICATION_AUDIT.md) before changing visibility.
