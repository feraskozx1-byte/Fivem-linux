#!/usr/bin/env python3
"""Validate the captured iterator sequence and replay only public PE arithmetic."""
from pathlib import Path
import json,re,struct
r=Path(__file__).resolve().parent
p=r/'private/index-sequence'
s=(p/'adh-index-trace.txt').read_text()
rows=[tuple(int(x,16) for x in m) for m in re.findall(r'LOOKUP n=(0x[0-9a-f]+) index=(0x[0-9a-f]+) buffer=(0x[0-9a-f]+) exportRVA=(0x[0-9a-f]+) names=(0x[0-9a-f]+)',s)]
assert len(rows)==1478
assert [x[1] for x in rows]==list(range(1478))
assert len({x[2:] for x in rows})==1
assert rows[0][4]==1468
assert 'fault_rva=0x0000000000d9fec5' in s and 'rax=0x0000000000130012' in s
assert 'TRACE_ERROR=0x0000000000000000' in s
assert 'INSTRUMENTATION_COUNT_CAP' not in s
export=(p/'rca-buffer-export.bin').read_bytes()
nf,nn,af,an,ao=struct.unpack_from('<IIIII',export,20)
assert nn==nf==1468 and an==0xcb718 and ao==0xcce08
tail=(p/'rca-buffer-tail.bin').read_bytes()
out_of_bounds=[]
for n,index,buf,er,names in rows[nn:]:
    offset=an+4*index
    word=struct.unpack_from('<I',tail,offset-(ao-64))[0]
    out_of_bounds.append({'index':index,'lookup_rva':hex(offset),'DWORD_interpreted_as_name_RVA':hex(word),'beyond_SizeOfImage':word>=0xd8000})
assert out_of_bounds[-1]['DWORD_interpreted_as_name_RVA']=='0x130012'
markers=[]
for path in p.glob('CitizenFX_log*'):
    for line in path.read_text(errors='replace').splitlines():
        if 'Adhesive failed to load under Wine (error ' in line:markers.append(line)
result=dict(
    new_fact='The observed lookup index is a sequential iterator0..1477, not an initial fixed index1477.',
    hardware_fixture_validated=json.loads((r/'fixture-validation.json').read_text())['passed'],
    lookup_count=len(rows),first_index=0,last_index=1477,consecutive_increment=1,
    same_buffer_and_export_directory_for_entire_sequence=True,
    table_NumberOfNames=nn,valid_index_range=[0,nn-1],first_semantically_invalid_index=nn,
    count_of_out_of_bounds_table_accesses_before_and_including_AV=len(out_of_bounds),
    fault_rva='0xd9fec5',fault_RVA_operand='0x130012',
    API_error998_markers=markers,debugger_trace_errors=0,debugger_instruction_cap_reached=False,
    out_of_bounds_table_reads=out_of_bounds,
    conclusions=['The first table-bound violation is at1468; the AV at1477 is later.',
        'Matching Windows name index1477 to RtlSetSecurityObjectEx does not identify a requested export.',
        'This trace rules out an immediate one-shot fixed index1477 in this observed path.',
        'The loop continued beyond NumberOfNames; why its continuation predicate allowed this remains unknown.'],
    not_proven=['An absent specific public API','Why the loop did not terminate at1468','A Wine API contract defect','Successful security initialization'],
    patch_created=False)
(r/'sequence-evidence.json').write_text(json.dumps(result,indent=2)+'\n')
short=s.splitlines()
look=[x for x in short if x.startswith('LOOKUP n=')]
excerpt=['First lookups:']+look[:4]+['Boundary and last lookups:']+look[nn-2:]+['Outcome:']+[x for x in short if x.startswith(('fault_rva=','rax=','LOOKUPS_TOTAL=','TRACE_ERROR=','RESULT='))]
(r/'sequence-excerpt.txt').write_text('\n'.join(excerpt)+'\n')
print(json.dumps(result,indent=2))
