import os
from Crypto.Cipher import ARC4
from rs.utils.formatters import bytes_to_rs
import string
import random

class RC4Encrypt:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def encode(self, plaintext):
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def imports(self):
        return ['extern crate rc4;',
                'use rc4::{KeyInit, Rc4, StreamCipher};'
                ]

    def compilerOptions(self):
        return ['rc4 = "0.2.0"']

    def codeblock(self):
        return f"""
fn {self.name}(encrypted_data: &[u8]) -> Vec<u8>{{
    {bytes_to_rs(self.key, 'key')}
    let mut plaintext = encrypted_data.to_vec();
    let mut rc4 = Rc4::new_from_slice(&key).unwrap();
    rc4.apply_keystream(&mut plaintext);

    plaintext.to_vec()
}}
"""

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')