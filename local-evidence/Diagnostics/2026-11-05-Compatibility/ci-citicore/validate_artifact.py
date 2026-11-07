#!/usr/bin/env python3
"""Check native CoreRT PE/PDB; optionally smoke-load on Windows; stage outputs.

Never invokes EarlyMode_Init, component factories, authentication or a game.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess

REQUIRED_EXPORTS = {'CoreRT_SetupSEHHandler', 'EarlyMode_Init', 'CoreSetExceptionOverride'}


def inspect_pe(path):
    data = path.read_bytes()
    assert data[:2] == b'MZ', 'Missing DOS header'
    pe = struct.unpack_from('<I', data, 60)[0]
    assert data[pe:pe + 4] == b'PE\0\0'
    machine, sections = struct.unpack_from('<HH', data, pe + 4)
    size, characteristics = struct.unpack_from('<HH', data, pe + 20)
    optional = pe + 24
    assert machine == 0x8664 and struct.unpack_from('<H', data, optional)[0] == 0x20b, 'Not Windows AMD64 PE32+'
    assert characteristics & 0x2000, 'Not a DLL'
    table = optional + size

    def offset(rva):
        for index in range(sections):
            location = table + index * 40
            virtual_size, virtual_address, raw_size, raw = struct.unpack_from('<IIII', data, location + 8)
            if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
                position = raw + rva - virtual_address
                assert raw <= position < raw + raw_size and position < len(data), 'RVA outside file data'
                return position
        raise AssertionError('Unmapped RVA: ' + hex(rva))

    def string(rva):
        start = offset(rva)
        return data[start:data.index(b'\0', start)].decode('ascii')

    def directory(index):
        return struct.unpack_from('<II', data, optional + 112 + index * 8)

    export_rva, _ = directory(0)
    export = offset(export_rva)
    count = struct.unpack_from('<I', data, export + 24)[0]
    names_rva = struct.unpack_from('<I', data, export + 32)[0]
    exports = [string(struct.unpack_from('<I', data, offset(names_rva) + index * 4)[0]) for index in range(count)]
    assert REQUIRED_EXPORTS <= set(exports), 'Missing CoreRT export'
    imports = []
    import_rva, _ = directory(1)
    if import_rva:
        position = offset(import_rva)
        while any(data[position:position + 20]):
            imports.append(string(struct.unpack_from('<I', data, position + 12)[0]))
            position += 20
    debug_rva, debug_size = directory(6)
    codeview = None
    if debug_rva:
        for index in range(debug_size // 28):
            entry = offset(debug_rva) + index * 28
            kind, length, _, raw = struct.unpack_from('<IIII', data, entry + 12)
            if kind == 2 and data[raw:raw + 4] == b'RSDS':
                codeview = {'guid': data[raw + 4:raw + 20].hex(), 'age': struct.unpack_from('<I', data, raw + 20)[0]}
    assert codeview, 'No RSDS record'
    return {'machine': 'AMD64', 'exports': exports, 'imports': imports, 'codeview': codeview,
            'sha256': hashlib.sha256(data).hexdigest()}


def verify_pdb(path, expected):
    data = path.read_bytes()
    assert data.startswith(b'Microsoft C/C++ MSF 7.00'), 'Unsupported PDB container'
    block, _, _, directory_size, _, block_map = struct.unpack_from('<IIIIII', data, 32)
    number = (directory_size + block - 1) // block
    directory_blocks = struct.unpack_from('<' + 'I' * number, data, block_map * block)
    stream_directory = b''.join(data[v * block:(v + 1) * block] for v in directory_blocks)[:directory_size]
    streams = struct.unpack_from('<I', stream_directory)[0]
    sizes = struct.unpack_from('<' + 'I' * streams, stream_directory, 4)
    position = 4 + streams * 4
    info = None
    for index, size in enumerate(sizes):
        number = 0 if size == 0xffffffff else (size + block - 1) // block
        blocks = struct.unpack_from('<' + 'I' * number, stream_directory, position)
        position += number * 4
        if index == 1:
            info = b''.join(data[v * block:(v + 1) * block] for v in blocks)[:size]
            break
    assert info and len(info) >= 28
    actual = {'age': struct.unpack_from('<I', info, 8)[0], 'guid': info[12:28].hex()}
    assert actual == expected, 'PDB GUID/age mismatch'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dll', type=Path, required=True)
    p.add_argument('--pdb', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--load', action='store_true')
    args = p.parse_args()
    result = inspect_pe(args.dll)
    assert result['sha256'] != 'b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013', 'Old unpatched CoreRT binary supplied'
    verify_pdb(args.pdb, result['codeview'])
    result['pdb_matches'] = True
    if args.load:
        assert os.name == 'nt', 'Native loader smoke check requires Windows'
        with os.add_dll_directory(str(args.dll.resolve().parent)):
            module = ctypes.WinDLL(str(args.dll.resolve()))
            for name in REQUIRED_EXPORTS:
                getattr(module, name)  # Resolve only; do not call startup/security APIs.
        result['windows_loader_smoke'] = 'passed'
    else:
        result['windows_loader_smoke'] = 'not run'
    result['source_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.source, text=True).strip()
    changed = ['code/client/citicore/DllGameComponent.Win32.cpp', 'code/client/citicore/SEHTableHandler.Win32.cpp',
               'code/client/citicore/EarlyMode.Win32.cpp', 'code/client/shared/XBRInit.cpp']
    result['source_sha256'] = {v: hashlib.sha256((args.source / v).read_bytes()).hexdigest() for v in changed}
    args.output.mkdir(parents=True, exist_ok=True)
    for source in [args.dll, args.pdb]:
        destination = args.output / source.name
        assert not destination.exists(), 'Refusing to replace staged output'
        shutil.copy2(source, destination)
    (args.output / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ['machine', 'imports', 'pdb_matches', 'windows_loader_smoke', 'sha256']}, indent=2))


if __name__ == '__main__':
    main()
