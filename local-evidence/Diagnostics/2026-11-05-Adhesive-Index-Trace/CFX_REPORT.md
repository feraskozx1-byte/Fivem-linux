# New observation: index1477 is reached by a sequential NTDLL name-table walk

Local draft; not submitted. Official Adhesive1.0.0.24769 SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b` remains unchanged.

A visible hardware-debugger trace of the existing offline FiveM diagnostic host recorded every entry at Adhesive+D9FDD5: **indexes0,1,2,...1477**,1478entries total. The buffer/export-directory identity stayed constant and NumberOfNames was1468 at every entry. This rules out an immediate fixed-index1477 lookup in this path.

The first invalid name-table read occurs at1468. It reads adjacent WORD ordinals0and1 as a DWORD RVA0x10000. The walk continues for10out-of-bounds table accesses, reaching ordinals18and19 and RVA0x130012 at1477. This produces the previously observed AV at D9FEC5, then loader error998. Some earlier invalid accesses land in readable memory; the AV is later than the first table-bound violation.

The trace was validated first on an independent5-call fixture with exact expected indexes and unchanged checksum/exit0. No remote code/memory patching, API-return substitution, debugger masking or exception swallowing was used. Only debugger-owned hardware-breakpoint events were handled; the actual AV was passed NOT_HANDLED. No public-server connection was attempted.

Please provide the iterator's termination contract and intended search identity, with the continuation predicate operands around indexes1467/1468. Is its limit derived from NumberOfNames, a different table, or a not-found search path? We have not identified a missing public API or shown a Wine API-contract violation. The Windows-reference identity at index1477 does not identify the target of this sequential walk.
