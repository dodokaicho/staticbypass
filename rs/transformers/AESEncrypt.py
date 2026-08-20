import os
from rs.utils.formatters import bytes_to_rs
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random

class AESEncrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(32)
        if 'iv' in arguments:
            self.iv = arguments['iv'].encode()
        else:
            self.iv = os.urandom(16)

    def imports(self) -> list[str]:
        return ["extern crate aes;", 
                "extern crate cbc;", 
                "use aes::cipher::{block_padding::Pkcs7, BlockModeDecrypt, KeyIvInit};",
                "type Aes256CbcDec = cbc::Decryptor<aes::Aes256>;"]

    def compilerOptions(self) -> list[str]:
        return ['cbc = "0.2.1"', 'aes = "0.9.2"']

    def encode(self, plaintext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def codeblock(self) -> str:
        return f"""
fn {self.name}(encrypted_data: &[u8]) -> Vec<u8>{{
    {bytes_to_rs(self.key, 'key')}
    {bytes_to_rs(self.iv, 'iv')}
    let mut plaintext = vec![0u8; encrypted_data.len()];
    let pt = Aes256CbcDec::new(&key.into(), &iv.into())
        .decrypt_padded_b2b::<Pkcs7>(&encrypted_data, &mut plaintext)
        .unwrap();

    pt.to_vec()
}}
"""