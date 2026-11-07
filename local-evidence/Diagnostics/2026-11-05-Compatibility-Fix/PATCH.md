# Patch status

No Wine API repair was justified by the independent contract suite: all48 checks pass. The only change to that test program was the correct Clang asynchronous exception flag; this is not a product fix.

A distinct CoreRT-only experiment was built successfully and tested under ../2026-11-05-Adhesive-Direct-Repair/. It restores unmodified NTDLL diagnostics under Wine by declining CoreRT HardErrorScope diagnostic hooks; no protection library, return values or selection policy are patched. This is a controlled hypothesis test, not a claimed Adhesive fix. The actual fullhost still fails at adhesive+0xD9FEC5 with998. Diagnostic CoreRT/PDB links were restored; the experimental patch was not adopted. See that directory's REPORT_AR.md and comparison.json.

All source/runtime files outside Diagnostics remain unchanged. No full-client build, ticket work or server connection is involved.
