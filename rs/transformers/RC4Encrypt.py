import os
from Crypto.Cipher import ARC4
from rs.utils.formatters import bytes_to_rs
import string
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def imports(self) -> list[str]:
        return ['extern crate rc4;',
                'use rc4::{KeyInit, Rc4, StreamCipher};'
                ]

    def compilerOptions(self) -> list[str]:
        return ['rc4 = "0.2.0"']

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encrypted_data: &[u8]) -> Vec<u8>{{
    {bytes_to_rs(self.key, 'key')}
    let mut plaintext = encrypted_data.to_vec();
    let mut rc4 = Rc4::new_from_slice(&key).unwrap();
    rc4.apply_keystream(&mut plaintext);

    plaintext.to_vec()
}}
"""