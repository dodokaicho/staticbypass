from utils.utils import bytes_to_rs
from common.transformers.RC4Encrypt import RC4EncryptBase

class RC4Encrypt(RC4EncryptBase):



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