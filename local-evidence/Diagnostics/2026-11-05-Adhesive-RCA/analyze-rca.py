#!/usr/bin/env python3
"""Recalculate the bounded PE lookup evidence from the saved snapshots."""
from pathlib import Path
import hashlib, json, re, struct

root = Path(__file__).resolve().parent
project = root.parents[1]
run = root/'private/export-table-provenance'
raw_path = project/'Diagnostics/2026-11-05-Compatibility/private/api-probe-cachyos/prefix/drive_c/windows/system32/ntdll.dll'
raw = raw_path.read_bytes()
report = (run/'rca-debug-result.txt').read_text()
def value(key):
    return int(re.search(r'^'+re.escape(key)+r'=(0x[0-9a-f]+)$', report, re.M)[1],16)
def u32(b,off): return struct.unpack_from('<I',b,off)[0]
def u64(b,off): return struct.unpack_from('<Q',b,off)[0]

pe = u32(raw,60)
image = u32(raw,pe+80)
er = u32(raw,pe+136)
directory = raw[er:er+40]  # This Wine PE has raw offsets equal to section RVAs.
nf,nn,af,an,ao = struct.unpack_from('<IIIII',directory,20)
stack = (run/'rca-stack-sample.bin').read_bytes()
index = value('rsi')
lookup = an+4*index
tail = (run/'rca-buffer-tail.bin').read_bytes()
candidate = u32(tail,lookup-(ao-64))
assert value('fault_rva') == 0xd9fec5
assert value('rax') == candidate == 0x130012
assert value('read_target') == value('r9')+candidate
assert u64(stack,0x20) == value('r9')
assert u64(stack,0x30) == er
assert u64(stack,0x40) == index == 1477
assert nn == nf == 1468 and index >= nn
assert lookup == ao+36
assert struct.unpack_from('<HH',tail,lookup-(ao-64)) == (18,19)
assert candidate >= image
matches = {}
for scope in ['buffer','live']:
    header = (run/f'rca-{scope}-header.bin').read_bytes()
    image_base_at = pe+48
    if scope == 'live':
        assert u64(header,image_base_at) == value('ntdll_base')
    header_ok = header==raw[:1024] if scope=='buffer' else (header[:image_base_at]==raw[:image_base_at] and header[image_base_at+8:]==raw[image_base_at+8:1024])
    matches[scope] = dict(header_exact_or_live_ImageBase_normalized=header_ok,
        export_directory=(run/f'rca-{scope}-export.bin').read_bytes()==directory,
        names_tail_and_ordinals=(run/f'rca-{scope}-tail.bin').read_bytes()==raw[ao-64:ao+64])
assert all(all(x.values()) for x in matches.values())
base = project/'Diagnostics/2026-11-05-Adhesive-Direct-Repair/fullhost-file-baseline-exception-excerpt.txt'
baseline = base.read_text()
assert 'rax=0000000000130012' in baseline and 'rsi=00000000000005c5' in baseline
assert 'D9FEC5' in baseline
probe = json.loads((root/'private/export-contract/summary.json').read_text())
assert probe['success'] and probe['pass_count']==10 and probe['fail_count']==0
trace = (run/'wine.log').read_text(errors='replace').splitlines()
scope = f"{value('child_pid'):04x}:{value('child_tid'):04x}:"
start = next(i for i,s in enumerate(trace) if s.startswith(scope) and 'dispatch_exception code=c0000005' in s)
selected = [(i+1,s) for i,s in enumerate(trace[start:start+85],start) if s.startswith(scope)]
excerpt = '\n'.join(f'wine.log:{n}: {s}' for n,s in selected[:40])+'\n'
(root/'exception-excerpt.txt').write_text(excerpt)
facts = dict(
    conclusion='Proven invalid NTDLL export-name lookup; upstream selection of index1477 remains unknown.',
    official_adhesive_sha256=json.loads((run/'summary.json').read_text())['hashes']['adhesive.dll'],
    ntdll_sha256=hashlib.sha256(raw).hexdigest(),
    debugger_instrumentation='visible, no remote writes/context changes; AV continued NOT_HANDLED',
    non_debugger_baseline_same_RVA_RAX_RSI=True,
    captured_fields=dict(index=index,number_of_names=nn,number_of_functions=nf,
        export_directory_rva=hex(er),name_table_rva=hex(an),ordinal_table_rva=hex(ao),
        invalid_name_lookup_rva=hex(lookup),ordinal_words=[18,19],
        mistaken_name_rva=hex(candidate),image_size=hex(image)),
    stack_slots_verified={'0x20':'r9 image base','0x30':'0xca000 export directory RVA','0x40':'1477 index'},
    remote_samples_match_original_ntdll=matches,
    measured_target_state='MEM_RESERVE 0x2000 / Protect0; same allocation as committed r9 region',
    independent_public_export_probe={'checks':10,'failures':0,'names_checked':1468,'GetProcAddress_mismatches':0},
    not_proven=['Why index1477 was selected','Which public Windows export was intended',
        'Wine API defect','Host/private ABI incompatibility','Full security initialization success'],
    rejected_explanation='Coincidental COFF string-table location does not supply the index; the captured DWORD comes from the ordinal table.',
    next_needed='Cfx diagnostic at the name-index producer: intended export identity, input table/count, and derivation of1477.'
)
(root/'evidence.json').write_text(json.dumps(facts,indent=2)+'\n')
print(json.dumps(facts,indent=2))
