# Follow-up: NTDLL export rank comparison, no general Wine API defect established

New native reference: Windows Server2022 x64, NTDLL10.0.20348.5622. This is a public PE/API reference, not certification of a supported FiveM client OS or the Windows build Adhesive targets.

Wine NTDLL has1468 named exports; this Windows reference has2457. Both name tables are lexically sorted. Of1408 common names,1405 have different absolute name-table indexes while their relative lexical order agrees. All2457 direct native named exports agree with GetProcAddress; previous Wine checks likewise found no resolver disagreements.

Index1477 is outside Wine's table. In this Windows reference it names RtlSetSecurityObjectEx, which is absent from the observed Wine table. **We have no evidence this is Adhesive's intended target.** Matching a numeric index in one Windows version does not establish resolver intent.

Read-only Ghidra access now succeeds and the saved program hash matches the official DLL. However, the saved function at D9DF40 covers only193bytes of the33006-byte unwind range and does not recover control flow to the D9FDE7 name-index use. We did not force control-flow edges or modify the saved program.

Please identify the input contract and producer of1477 before D9FDEE: name index, hint, ordinal or another value; intended public export name; source table/build/count; and lookup failure handling. This will distinguish a missing required public API from an assumption about a particular NTDLL layout or another private initializer defect. No library/security changes or speculative Wine patch have been made. No binary or private log is attached; this draft has not been sent.
