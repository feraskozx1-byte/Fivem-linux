#!/usr/bin/env python3
"""Check signed SHA256 content on these local PE files; does not verify CA trust.

The sequential-file PE digest excludes CheckSum, the security-directory entry,
and the certificate table. Agreement with the authenticated DigestInfo validates
this layout for the inspected files. This is not a general Authenticode tool.
"""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

root = Path(__file__).resolve().parent
project = root.parents[1]
native = Path.home() / 'Games/FiveM-Official-Test/GTA-Prefix-Work/drive_c/windows/system32'
paths = [project / 'Official-Reference/adhesive-24769.dll'] + [native / n for n in
         ['msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll', 'ucrtbase.dll']]
rows = []
sha256_info = bytes.fromhex('3031300d060960864801650304020105000420')
for path in paths:
    data = path.read_bytes()
    pe = struct.unpack_from('<I', data, 60)[0]
    optional = pe + 24
    assert data[pe:pe+4] == b'PE\0\0'
    assert struct.unpack_from('<H', data, optional)[0] == 0x20b
    security = optional + 112 + 32
    offset, size = struct.unpack_from('<II', data, security)
    length = struct.unpack_from('<I', data, offset)[0]
    assert optional+68 < security < offset < len(data) and offset+size <= len(data)
    assert length <= size
    signature = data[offset+8:offset+length]
    result = subprocess.run(['openssl', 'smime', '-verify', '-inform', 'DER', '-noverify'],
                            input=signature, capture_output=True)
    content = result.stdout
    assert result.returncode == 0 and content[-51:-32] == sha256_info
    digest = hashlib.sha256(data[:optional+64] + data[optional+68:security] +
                            data[security+8:offset] + data[offset+size:]).digest()
    row = dict(path=str(path), pkcs7_signature_verified_without_chain=True,
               sha256_pe_digest=digest.hex(), content_sha256_digest=content[-32:].hex(),
               digest_matches=digest == content[-32:], trust_chain_verified=False)
    rows.append(row)
    assert row['digest_matches'], str(path)
(root / 'signature-checks.json').write_text(json.dumps(rows, indent=2)+'\n')
print('All five image digests match cryptographically verified signed content; CA trust/revocation not checked.')
