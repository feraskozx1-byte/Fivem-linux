| Test | CoreRT | VC runtime / UCRT | CoreRT exceptions | Missing MSVCP imports | First probe-thread fault | Read target | Load result |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| old-builtin-1 | old | built-in / built-in | 0 | 8 | Adhesive+0xD9FEC5 | 0xa5d1ca | 998 / failed |
| new-builtin-1 | new | built-in / built-in | 0 | 8 | Adhesive+0xD9FEC5 | 0xa5befa | 998 / failed |
| new-native-vc-1 | new | native / built-in | 0 | 0 | Adhesive+0xD9FEC5 | 0xa4d50a | 998 / failed |
| new-builtin-repeat | new | built-in / built-in | 0 | 8 | Adhesive+0xD9FEC5 | 0xa5befa | 998 / failed |
| new-native-vc-ucrt-1 | new | native / native | 0 | 0 | Adhesive+0xD9FEC5 | 0xa4fb1a | 998 / failed |

All are standalone initialization-host tests. Same failure offset, varying invalid pointer addresses, PROCESS_ATTACH and `_initterm` chain. Native UCRT frame is `_initterm+0x4F`; built-in UCRT frame is `_initterm+0x2A`. No component factory or normal security startup was exercised. See `trace-excerpts.txt` for original line numbers and `results.json` for per-test evidence.
