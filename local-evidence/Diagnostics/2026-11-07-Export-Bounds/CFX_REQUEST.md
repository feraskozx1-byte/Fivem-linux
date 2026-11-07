# Vendor diagnostic request: NTDLL export iterator no-match/bound contract

Local draft; not submitted. No DLL, private memory samples, credentials, tickets, or user paths attached.

Adhesive1.0.0.24769, SHA256`3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`, fails during DLL_PROCESS_ATTACH under Wine11.0/CachyOS. Earlier producer tracing established index0→1477 by repeated previous-index+1, with the first out-of-range index1468 for NumberOfNames1468. This request concerns why iteration continues, rather than the final AV location alone.

New measurements:

- Native Windows Server2022 NTDLL metadata and Wine both place the ordinal table immediately after the name-pointer table. The next DWORD is nonzero in both. There is no observed Windows-specific NULL sentinel missing in Wine. Both tables have valid bounds/order in the checked metadata. Different sets of exported names remain possible upstream triggers, not an identified target.
- A new independent Wine fixture correctly handles missing and case-mismatched names via GetProcAddress and LdrGetProcedureAddress. It passes8checks, and validates the observer against10paired interface events and4known read accesses. No Adhesive or TLS test is involved.
- In the real client, a visible hardware read/write watchpoint on the copied export directory's NumberOfNames field, armed at first lookup/index0, records **zero accesses on the observed initializer thread through the AV**. At the AV the field still contains1468, the same buffer is used, and the4-byte watchpoint remains enabled.
- No NTDLL-resolution event via the two monitored standard interfaces occurs between the first lookup and the fault. Earlier observed failures originate in CoreRT's existing ZwQueryDebugFilterState probes, not a visible caller in Adhesive. Coverage is the observed initialization thread and interfaces, not every possible helper/custom resolver.
- The fault remains index1477, name RVA0x130012, Adhesive RVA0xD9FEC5 and loader error998. The official DLL is unchanged. The previous TLS return-status correction has separately been shown not to resolve this failure.

**Please provide a vendor-approved diagnostic for just these public-interface facts:**

1. Which public Windows/NTDLL export is the initializer trying to find? If the internal representation is encoded, the final public API identifier is sufficient; its algorithm/key is not requested.
2. What effective name-index bound or termination condition applies at1467→1468, where was it obtained/cached, and what is the intended no-match result for an unsupported/missing export?
3. For the same Adhesive build on a supported native Windows client, what is that requested export's successful name/index and effective bound? Our native reference currently covers NTDLL metadata, **not** a native Adhesive initialization comparison.

These values distinguish a missing implementable public API from incorrect lookup input or a proprietary initializer assumption. An observed count of1468 alone does not prove the code has no cached bound. We have not modified comparisons, injected exports, padded/reordered a table, suppressed an AV, hidden Wine, or changed authentication/security decisions. No claim of successful security initialization is made.
