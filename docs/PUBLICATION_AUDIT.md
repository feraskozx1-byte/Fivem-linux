# Public release audit — 2026-11-07

**Review status: NOT FULLY CLEARED FOR MAKING THIS ORIGINAL REPOSITORY PUBLIC.**

This is a provenance and security review, **not a legal opinion**. A private repository can contain historical source and diagnostics that are inappropriate for a public repository even when the research itself is publishable.

## Files reviewed

- The current repository tree and text/source inventory: **180 files under `local-evidence/`** (179 initially imported evidence files plus the index README), and the project's documentation/configuration.
- Every current text/source file was subjected to a heuristic scan for GitHub personal access tokens, long credential assignments, private key markers, home paths and email addresses.
- The large copied Wine NTDLL loader, original MinHook header, FiveM-derived source and PR #4050 patch were reviewed for license attribution.
- Relevant published upstream license files were verified from [FiveM](https://github.com/citizenfx/fivem/blob/master/LICENSE), [Wine](https://github.com/wine-mirror/wine/blob/master/COPYING.LIB), and [MinHook](https://github.com/TsudaKageyu/minhook/blob/master/LICENSE.txt).

## Findings

| Finding | Result |
| :-- | :-- |
| Original GTA V / official Adhesive binaries | Not present in the text-only archive |
| GitHub PATs / obvious long password assignments / private keys | **No matches in the scanned current files** — not a guarantee |
| Local user paths | Present, including `/home/feras/` in historic reports/scripts |
| Contributor email | Present in the captured upstream Git-format patch header |
| Full copy of Wine `loader.c` | Present; LGPL 2.1-or-later applies |
| FiveM source & patch snippets | Present; specific paths are LGPL 2.0 except for third-party and other licensed material |
| MinHook header | Present, with original source redistribution notice |
| Patch that changes Wine/protection handling | Present in `PR-4050.patch`; additional platform-terms assessment needed |
| Entire history clean for unrestricted publication | **Not proven** |
| Administrative publishing permission in connected GitHub tool | **Unavailable** |

## Legal/technical preparation completed

- Added [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md), recording upstream authors and file-level licenses.
- Added full texts in [LICENSES/](../LICENSES/): LGPL 2.0, LGPL 2.1 and MinHook redistribution conditions.
- Kept the project labeled as historical research with **no working protected public-server compatibility**.
- Did not include a blanket root LICENSE that could misleadingly claim ownership over upstream code.

## Why the original archive is higher-risk to publish

GitHub's [visibility documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility) states that converting Private → Public makes source, activity, and Actions history available to everyone, and people may fork it.

**Deleting or rewriting a file in the newest commit is not sufficient** to assure private information in old commits is gone. The source history contains raw patches, local paths, and references to platform protection compatibility experiments. Automated token scanning cannot establish full legal compliance or absence of all private data.

## Recommended publication path

**Lower-risk choice:** keep this original full-history research archive **Private** and publish a **new, clean-history Public repository** containing curated original README/docs, tested nonproprietary fixtures, and only source/patch material with verified licensing and no personal information. Preserve this private project as the historical source of truth.

**If the owner elects to publish the exact original archive:** they should review **every commit and historical Actions log**, accept the exposure of local identifiers and raw tests, and consider legal advice about platform terms before making it Public. These steps cannot be completed by a heuristic scan alone.

## Visibility action

The currently connected GitHub app does **not** expose the repository-administration operation to change visibility. The owner can use GitHub's own web UI at **Settings → Danger Zone → Change repository visibility → Public**, but this review does **not** recommend that operation on the existing raw-history repository without additional checks.

*No conclusion here guarantees the absence of takedowns, license complaints or claims.*
