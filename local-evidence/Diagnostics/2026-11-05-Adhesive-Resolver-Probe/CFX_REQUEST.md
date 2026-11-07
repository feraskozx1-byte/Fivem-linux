# Request for authorized resolver diagnostics, Adhesive24769

Local draft only; not submitted. Official DLL unchanged, SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`.

After the previously demonstrated NTDLL name-index sequence0..1477 with NumberOfNames1468, we instrumented candidate comparison sites using visible hardware breakpoints, validated on an independent11-event fixture with checksum/exit0. No code bytes or API return values were changed.

New facts:

- DA3795 compares a one-time setup value22000 with10240 before the name scan; it is not the repeatedly executed name-index bound. DA5123 was not reached.
- DA4FC2 is reached1477times, associated with indexes0..1476. None of those comparisons is equal, including all1468declared valid NTDLL entries. DA006C is not reached.
- The subsequent read still faults at D9FEC5 with RVA operand0x130012, followed by loader error998.

Please identify the semantic target of DA4FC2 and its continuation/return contract: what identity or value is expected to match, and how should the routine handle no match/end-of-name-table? We cannot identify a specific missing public API from the observed values alone. A diagnostic build reporting that target and boundary condition, or authorized matching symbols, would enable a causally linked general Wine reproducer/implementation.

No matching local PDB was found; the documented symbol-server path for this GUID/age returned401. No attempt to bypass access control was made. No proprietary binary, private log, authentication data, or server connection is attached.
