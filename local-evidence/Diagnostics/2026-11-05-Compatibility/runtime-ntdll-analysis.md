# Actual second-Epic CachyOS ntdll analysis

Read-only inspection on 2026-11-05. No runner execution, prefix initialization, binary patching or configuration writes.

File: `/home/feras/.var/app/com.heroicgameslauncher.hgl/config-epic2/heroic/tools/proton/Proton-CachyOS-latest/files/lib/wine/x86_64-windows/ntdll.dll`

SHA-256: `af292382429047a793ced19c8740a08ee1a8b95711cfec2eda4b5fb5dcc762c5`

Runner version: `1792530497 cachyos-11.0-20261015-slr`

PE: COFF x86-64; preferred image base `0x170000000`; `.text` RVA `0x1000`, executable/readable. Addresses below are preferred VAs, not live process addresses.

Exports verified with `llvm-readobj --file-headers --coff-exports`:

| Export | RVA |
|---|---|
| RtlLookupFunctionTable | 0x37F80 |
| RtlLookupFunctionEntry | 0x37D40 |
| RtlImageDirectoryEntryToData | 0x31FD0 |
| RtlAddFunctionTable | 0x1DA30 |

## Confirmed behavior

- `RtlLookupFunctionTable` uses the public three-argument x64 ABI: RCX=PC, RDX=image base pointer, R8=length pointer. It saves RDX to RBX and R8 to RSI, calls `LdrFindEntryForAddress`, writes the module base to the caller's base pointer, then calls `RtlImageDirectoryEntryToData(moduleBase, TRUE, 3, length)`.
- The length is bytes, not runtime-function count. The directory helper loads PE DataDirectory.Size and writes it directly to the output (`0x170032030-34`); x64 `RtlLookupFunctionEntry` converts it to count using multiply `0xAAAAAAAB`, shift 35 (division by 12, the size of RUNTIME_FUNCTION).
- Crucially, this actual runner's `RtlLookupFunctionEntry` has the table lookup **inlined**. At `0x170037D5B` it calls `LdrFindEntryForAddress`, then at `0x170037D88` it calls `RtlImageDirectoryEntryToData` directly. It never calls exported `RtlLookupFunctionTable`. Therefore hooking only that public export would miss this runner's unwind lookups, even though upstream C source contains a call to it.
- This runner's `virtual_unwind` calls `RtlLookupFunctionEntry` at `0x17008A2D5`; frame-walk helpers also call the entry export. Both table and entry implementations share the actual non-inlined `RtlImageDirectoryEntryToData` entrypoint.
- Before requesting the directory, `RtlLookupFunctionEntry` writes `LDR_DATA_TABLE_ENTRY.DllBase` to the caller's image base pointer. It passes that same DllBase to the directory helper. Thus the directory hook's exact-module-base match and table RVA base agree; the hook need not replace that caller output.

## Source fix chosen from this evidence

The early Wine branch hooks only the existing `RtlImageDirectoryEntryToDataStub`, avoiding a second hook and Windows-private helper heuristics. The stub overrides only the designated game module's exception directory for mapped-image requests; other modules, directories and raw-file requests forward to the original. It returns the stored table and its size in bytes. This covers both direct table lookups and this compiler-inlined entry lookup without depending on compiler inlining policy.

The source now checks export lookup and MinHook creation/enabling, enabling only this target. Existing Windows downlevel lookup remains in use on its native path.

## Hookability evidence and limits

`RtlImageDirectoryEntryToData` begins with simple complete instructions: `push rbp; push r12; push rdi; push rsi; push rbx; sub rsp,0x20; lea rbp,[rsp+0x20]`. First 15 bytes contain no relative branch or RIP-relative operand. This appears statically suitable for a MinHook trampoline; `RtlLookupFunctionTable` likewise starts with ordinary register pushes/stack adjustment. Actual memory protection changes, nearby trampoline allocation and live hook activation were not tested. A passing static inspection is not proof that MinHook will succeed in a real process.

Selected disassembly, obtained with `llvm-objdump --disassemble-symbols=RtlLookupFunctionTable,RtlLookupFunctionEntry,RtlImageDirectoryEntryToData,virtual_unwind --x86-asm-syntax=intel`:

```asm
170031fd0: 55                          	push	rbp
170031fd1: 41 54                       	push	r12
170031fd3: 57                          	push	rdi
170031fd4: 56                          	push	rsi
170031fd5: 53                          	push	rbx
170031fd6: 48 83 ec 20                 	sub	rsp, 0x20
170031fda: 48 8d 6c 24 20              	lea	rbp, [rsp + 0x20]
170031fdf: 31 c0                       	xor	eax, eax
170031fe1: 41 89 d4                    	mov	r12d, edx
170031fe4: f6 c1 01                    	test	cl, 0x1
170031fe7: 48 89 cb                    	mov	rbx, rcx
170031fea: 44 89 c6                    	mov	esi, r8d
170031fed: 44 0f 45 e0                 	cmovne	r12d, eax
170031ff1: 48 83 e3 fc                 	and	rbx, -0x4
170031ff5: 4c 89 cf                    	mov	rdi, r9
170031ff8: 48 89 d9                    	mov	rcx, rbx
170031ffb: e8 c0 00 00 00              	call	0x1700320c0 <RtlImageNtHeader>
170032000: 48 89 c2                    	mov	rdx, rax
170032003: 48 85 c0                    	test	rax, rax
170032006: 74 6f                       	je	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
170032008: 0f b7 40 18                 	movzx	eax, word ptr [rax + 0x18]
17003200c: 66 3d 0b 02                 	cmp	ax, 0x20b
170032010: 0f 84 8a 00 00 00           	je	0x1700320a0 <RtlImageDirectoryEntryToData+0xd0>
170032016: 66 3d 0b 01                 	cmp	ax, 0x10b
17003201a: 75 5b                       	jne	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
17003201c: 0f b7 f6                    	movzx	esi, si
17003201f: 3b 72 74                    	cmp	esi, dword ptr [rdx + 0x74]
170032022: 73 53                       	jae	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
170032024: 48 83 c6 0e                 	add	rsi, 0xe
170032028: 8b 4c f2 08                 	mov	ecx, dword ptr [rdx + 8*rsi + 0x8]
17003202c: 85 c9                       	test	ecx, ecx
17003202e: 74 47                       	je	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
170032030: 8b 44 f2 0c                 	mov	eax, dword ptr [rdx + 8*rsi + 0xc]
170032034: 89 07                       	mov	dword ptr [rdi], eax
170032036: 45 85 e4                    	test	r12d, r12d
1700320a0: 0f b7 f6                    	movzx	esi, si
1700320a3: 3b b2 84 00 00 00           	cmp	esi, dword ptr [rdx + 0x84]
1700320a9: 73 cc                       	jae	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
1700320ab: 48 83 c6 10                 	add	rsi, 0x10
1700320af: 8b 4c f2 08                 	mov	ecx, dword ptr [rdx + 8*rsi + 0x8]
1700320b3: 85 c9                       	test	ecx, ecx
1700320b5: 0f 85 75 ff ff ff           	jne	0x170032030 <RtlImageDirectoryEntryToData+0x60>
1700320bb: eb ba                       	jmp	0x170032077 <RtlImageDirectoryEntryToData+0xa7>
170037d40: 55                          	push	rbp
170037d41: 41 55                       	push	r13
170037d43: 41 54                       	push	r12
170037d45: 57                          	push	rdi
170037d46: 56                          	push	rsi
170037d47: 53                          	push	rbx
170037d48: 48 83 ec 38                 	sub	rsp, 0x38
170037d4c: 48 8d 6c 24 30              	lea	rbp, [rsp + 0x30]
170037d51: 48 89 d6                    	mov	rsi, rdx
170037d54: 48 8d 55 f8                 	lea	rdx, [rbp - 0x8]
170037d58: 48 89 cb                    	mov	rbx, rcx
170037d5b: e8 e0 cb fd ff              	call	0x170014940 <LdrFindEntryForAddress>
170037d60: 89 c7                       	mov	edi, eax
170037d62: 85 c0                       	test	eax, eax
170037d64: 0f 85 c6 00 00 00           	jne	0x170037e30 <RtlLookupFunctionEntry+0xf0>
170037d6a: 48 8b 45 f8                 	mov	rax, qword ptr [rbp - 0x8]
170037d6e: 4c 8d 4d f4                 	lea	r9, [rbp - 0xc]
170037d72: 41 b8 03 00 00 00           	mov	r8d, 0x3
170037d78: 48 8b 50 30                 	mov	rdx, qword ptr [rax + 0x30]
170037d7c: 48 89 16                    	mov	qword ptr [rsi], rdx
170037d7f: 48 8b 48 30                 	mov	rcx, qword ptr [rax + 0x30]
170037d83: ba 01 00 00 00              	mov	edx, 0x1
170037d88: e8 43 a2 ff ff              	call	0x170031fd0 <RtlImageDirectoryEntryToData>
170037d8d: 49 89 c1                    	mov	r9, rax
170037d90: 48 85 c0                    	test	rax, rax
170037d93: 0f 84 97 00 00 00           	je	0x170037e30 <RtlLookupFunctionEntry+0xf0>
170037d99: 8b 45 f4                    	mov	eax, dword ptr [rbp - 0xc]
170037d9c: ba ab aa aa aa              	mov	edx, 0xaaaaaaab
170037da1: 4c 8b 16                    	mov	r10, qword ptr [rsi]
170037da4: 48 0f af c2                 	imul	rax, rdx
170037da8: 48 c1 e8 23                 	shr	rax, 0x23
170037dac: 44 8d 40 ff                 	lea	r8d, [rax - 0x1]
170037db0: 85 c0                       	test	eax, eax
170037db2: 75 15                       	jne	0x170037dc9 <RtlLookupFunctionEntry+0x89>
170037f80: 55                          	push	rbp
170037f81: 56                          	push	rsi
170037f82: 53                          	push	rbx
170037f83: 48 83 ec 30                 	sub	rsp, 0x30
170037f87: 48 8d 6c 24 30              	lea	rbp, [rsp + 0x30]
170037f8c: 48 89 d3                    	mov	rbx, rdx
170037f8f: 48 8d 55 f8                 	lea	rdx, [rbp - 0x8]
170037f93: 4c 89 c6                    	mov	rsi, r8
170037f96: e8 a5 c9 fd ff              	call	0x170014940 <LdrFindEntryForAddress>
170037f9b: 89 c2                       	mov	edx, eax
170037f9d: 31 c0                       	xor	eax, eax
170037f9f: 85 d2                       	test	edx, edx
170037fa1: 75 22                       	jne	0x170037fc5 <RtlLookupFunctionTable+0x45>
170037fa3: 48 8b 45 f8                 	mov	rax, qword ptr [rbp - 0x8]
170037fa7: 49 89 f1                    	mov	r9, rsi
170037faa: 41 b8 03 00 00 00           	mov	r8d, 0x3
170037fb0: 48 8b 50 30                 	mov	rdx, qword ptr [rax + 0x30]
170037fb4: 48 89 13                    	mov	qword ptr [rbx], rdx
170037fb7: 48 8b 48 30                 	mov	rcx, qword ptr [rax + 0x30]
170037fbb: ba 01 00 00 00              	mov	edx, 0x1
170037fc0: e8 0b a0 ff ff              	call	0x170031fd0 <RtlImageDirectoryEntryToData>
170037fc5: 48 83 c4 30                 	add	rsp, 0x30
170037fc9: 5b                          	pop	rbx
170037fca: 5e                          	pop	rsi
170037fcb: 5d                          	pop	rbp
170037fcc: c3                          	ret
17008a280: 55                          	push	rbp
17008a281: 41 57                       	push	r15
17008a283: 41 56                       	push	r14
17008a285: 41 55                       	push	r13
17008a287: 41 54                       	push	r12
17008a289: 57                          	push	rdi
17008a28a: 56                          	push	rsi
17008a28b: 53                          	push	rbx
17008a28c: 48 81 ec b8 01 00 00        	sub	rsp, 0x1b8
17008a293: 48 8d ac 24 80 00 00 00     	lea	rbp, [rsp + 0x80]
17008a29b: 48 c7 45 f8 00 00 00 00     	mov	qword ptr [rbp - 0x8], 0x0
17008a2a3: 89 cf                       	mov	edi, ecx
17008a2a5: 48 89 d3                    	mov	rbx, rdx
17008a2a8: 4c 89 c6                    	mov	rsi, r8
17008a2ab: 45 85 c9                    	test	r9d, r9d
17008a2ae: 0f 85 d4 00 00 00           	jne	0x17008a388 <virtual_unwind+0x108>
17008a2b4: 48 c7 43 08 00 00 00 00     	mov	qword ptr [rbx + 0x8], 0x0
17008a2bc: 4c 8b 43 40                 	mov	r8, qword ptr [rbx + 0x40]
17008a2c0: 48 8d 53 08                 	lea	rdx, [rbx + 0x8]
17008a2c4: c7 43 48 00 00 00 00        	mov	dword ptr [rbx + 0x48], 0x0
17008a2cb: 48 8b 8e f8 00 00 00        	mov	rcx, qword ptr [rsi + 0xf8]
17008a2d2: 48 89 0b                    	mov	qword ptr [rbx], rcx
17008a2d5: e8 66 da fa ff              	call	0x170037d40 <RtlLookupFunctionEntry>
17008a2da: 48 89 43 10                 	mov	qword ptr [rbx + 0x10], rax
17008a2de: 49 89 c1                    	mov	r9, rax
```


Session execution update: subsequent offline UMU/CachyOS experiments were run by the primary agent in a new isolated prefix. See [EXPERIMENTS_AR.md](EXPERIMENTS_AR.md) and [live-probe-results.txt](live-probe-results.txt). The SEH strategy probe and ABI probe passed; initialized Adhesive load failed with error 998 at adhesive+0xD9FEC5. These are standalone diagnostics, not a rebuilt CoreRT/MinHook/full-client test. Existing runtime binaries and accounts were preserved.
