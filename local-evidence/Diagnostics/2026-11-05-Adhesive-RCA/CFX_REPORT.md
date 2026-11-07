# Official Adhesive 24769: invalid NTDLL export-name index during PROCESS_ATTACH

Local draft only; not submitted. No account data, tickets, server addresses, binary attachments, or proprietary decompilation.

Official adhesive.dll 1.0.0.24769, SHA256 `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b`, on Wine11.0 / Proton-CachyOS `cachyos-11.0-20261015-slr`, Ubuntu x86-64. FiveM PR4050 host. The previous no-debugger host failure and the new visible read-only debugger observation have the same fault RVA, RAX/RSI and initializer stack.

New evidence, captured at first chance before unwind:

- R9 points to an NTDLL image buffer. Its first1024bytes match the Wine system32 NTDLL. Its export directory and sampled name/ordinal boundary match both the live NTDLL and the on-disk module. Live ImageBase reflects relocation, as expected.
- Export directory RVA=`0xCA000`; NumberOfNames=NumberOfFunctions=`1468`; AddressOfNames=`0xCB718`; AddressOfNameOrdinals=`0xCCE08`.
- ESI and stack+0x40=`1477`; stack+0x20=R9, stack+0x30=`0xCA000`.
- The bounded instruction dataflow at Adhesive RVAs D9FDDF/D9FDE7/D9FDEE loads the name-table RVA and performs a DWORD name-pointer lookup with this index. Its address is `0xCB718+1477*4=0xCCE2C`, already beyond the1468-entry name table.
- This location contains WORD ordinals18 and19. Interpreted as a DWORD name RVA, they become `0x130012`, matching RAX exactly. The subsequent byte read at D9FEC5 uses R9+RAX, beyond SizeOfImage=`0xD8000`. VirtualQueryEx reports that target MEM_RESERVE/Protect0.
- Loader unwind returns PROCESS_ATTACH failure, followed by LoadLibrary error998. No exception is swallowed by the diagnostic debugger. Library/security behavior was not patched.

An independent public PE test validates all1468 named exports against GetProcAddress: zero structural failures, zero address disagreements. It reproduces the invalid lookup arithmetic from the captured index without dereferencing the invalid RVA. It does **not** establish how Adhesive selected1477 or prove a Wine API defect. No native Windows comparison was performed in this stage.

Please identify the intended public Windows export and the provenance/contract of index1477 at this initializer's lookup. Is it a name-table index, an ordinal converted to an index, a build-specific assumption, or a not-found path? A diagnostic build reporting the intended export identity, selected index, and source table/count would distinguish a missing public API from a resolver/input-contract issue. Please also confirm the supported host/component ABI for this Adhesive hash.

We have not changed Adhesive, masked Wine, manufactured exports, altered security checks, expanded the failing allocation, or treated Sticky as success. The upstream producer of1477 remains unresolved; a general Wine patch is not currently justified.
