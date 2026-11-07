# Unresolved blockers / project stop point

## Blocker A — the official protection library does not initialize on Wine

Observed: official `adhesive.dll` 1.0.0.24769 raises `0xC0000005` around `D9FEC5` during `DLL_PROCESS_ATTACH`; FiveM records loader error 998 and falls back to Sticky.

What is known: a manual NTDLL export-name iteration exceeds the 1468-name table and reaches an invalid RVA. Static-TLS loader API return differences did not cause the observed crash.

What is **not** known: the exact public export being requested, the cached termination bound, or why this initialization path does not stop at the name-count boundary under Wine. A Wine/Windows export-count difference is insufficient to name the specific mismatch.

## Blocker B — official secure network behavior

Even if the DLL were made to load successfully, the client would still have to demonstrate normal authentication, protected resource loading and security functionality. The fallback `sticky` component and the absence of a verified `cfxTicket2` remain inadequate for public servers. No public-server compatibility is claimed.

## Blocker C — host test constraints

Ubuntu ran on a modified PS5 with a very slow external USB HDD; full builds, repeated multi-gigabyte copies and giant debug logs significantly increased turnaround time. Windows VM experiments did not provide a useful alternative.

## Project decision

The experiment is **paused**, not declared technically impossible. No validated compatibility patch solves the root fault. No protection bypass, fake authentication ticket, hidden Wine detection, or altered proprietary binary is included.

## Requirements for a legitimate future iteration

A genuinely new, independently verifiable Windows API incompatibility tied to the fault; a source-backed Wine fix; and a regression test that proves the original protection functionality rather than merely suppressing the exception. Official vendor clarification would be valuable but is not represented as a prerequisite for independent research.
