# Hypotheses and scope

| Hypothesis | Connection to recorded failure | Independent contract test | Missing causal evidence |
| --- | --- | --- | --- |
| Reserve/commit or protection semantics wrong | Actual-host target lay in last-recorded uncommitted subrange | Reserve, partial commit, cross-range VirtualProtect atomic failure, zero-on-recommit, own read/write AVs | No demonstrated wrong API output in Adhesive |
| malloc/realloc size or ownership wrong | Fault r9 numerically matches a prior malloc request | malloc(0xD8000), _msize, x64 alignment, full requested interval, preserving realloc | Does not identify Adhesive object lifetime/index source |
| File short-read count wrong | Earlier trace lacked returned counts | Exact/rounded/tail/EOF reads of an owned deterministic fixture, IOSB counts and canary | Synthetic fixture is not the actual input; direct actual-file replay is recorded separately |
| CRT initializer walking/exception propagation wrong | _initterm lies in observed initializer stack | Ordered callbacks, null entries, early nonzero _initterm_e, own raised exception | Does not reproduce closed initializer behavior |
| Ordinary loader error handling wrong | Adhesive returns failed PROCESS_ATTACH with998 | Own successful, FALSE-returning and AV fixtures; refcount/unload | AV998 is observed, not a native-Windows verified universal mapping |
| SEH failure | Access violation during initialization | Compiler emits asynchronous EH; own reserved/read-only memory faults | Original harness omitted -fasync-exceptions; corrected as test tooling, not Wine |

The real-host direct experiment and actual ntdll/win32u transaction replay are in ../2026-11-05-Adhesive-Direct-Repair/. No test here calls FiveM or Adhesive.
