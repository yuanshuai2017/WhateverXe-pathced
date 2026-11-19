#!/usr/bin/env python3
"""Replay qualified ADL-S Combo clock translations in the real donor code."""
from pathlib import Path
import hashlib,re,struct,subprocess,sys,tempfile
r=Path(__file__).resolve().parents[1]
b=bytearray(Path(sys.argv[1]).read_bytes())
# Also accept the exact Tahoe Graphics 0.4.4 donor used for this TC3 replay.
assert hashlib.sha256(b).hexdigest() in {
    'c004fc1ac9ee4157e2e12736f40fa6639bde025a279326beeb9dd48c9b445731',
    '115a4616e862228a8c82df6e52ba41ac02b9750f116352ff3575aadcc950888e',
}
s=(r/'WhateverXe/kern_xe.cpp').read_text()
def tc3(suffix):
    match=re.search(r'const uint8_t adlsClockTC3'+suffix+r'\[\]=\{([^}]+)\}',s)
    return bytes(int(x,0) for x in match.group(1).split(','))
assert b[0x6d209:0x6d21c]==tc3('Find')
assert b[0x6d778:0x6d77e]==bytes.fromhex('ff9030010000')
assert b[0x6dcfa:0x6dd00]==bytes.fromhex('ff9130010000')
for name,off in [('On',0x6cfd3),('Select',0x6d222),('SelectC',0x6d219),('SelectCPLL',0x6d4a2),('Off',0x6dca8),('Bus',0x53b66)]:
    def array(suffix):
        v=re.search(r'const uint8_t adlsClock'+name+suffix+r'\[\]=\{([^}]+)\}',s).group(1)
        return bytes(int(n,0) for n in v.split(','))
    before,after=array('Find'),array('Replace')
    assert len(before)==len(after) and b[off:off+len(before)]==before
    b[off:off+len(after)]=after
b[0x6d209:0x6d21c]=tc3('Replace')
before=[0x164000,0x164080,0x164200,0x164004,0x164084,0x164204]
assert list(struct.unpack_from('<6Q',b,0x9a0e8))==before
struct.pack_into('<6Q',b,0x9a0e8,0x164284,0x16428c,0x164294,0x164288,0x164290,0x164298)
with tempfile.TemporaryDirectory(prefix='adls-clock-') as d:
    d=Path(d);(d/'donor').write_bytes(b)
    subprocess.run(['clang++','-arch','x86_64','-std=c++17','-O1','-g','-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer','-I'+str(r/'WhateverXe'),str(r/'tests/adls_clock_native_fixture.cpp'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test'),str(d/'donor')],check=True)
