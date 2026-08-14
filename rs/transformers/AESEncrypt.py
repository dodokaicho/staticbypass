from utils.utils import bytes_to_rs
from common.transformers.AESEncrypt import AESEncryptBase

class AESEncrypt(AESEncryptBase):

    def imports(self):
        return ["extern crate aes;", 
                "extern crate cbc;", 
                "use aes::cipher::{block_padding::Pkcs7, BlockModeDecrypt, KeyIvInit};",
                "type Aes256CbcDec = cbc::Decryptor<aes::Aes256>;"]

    def compilerOptions(self):
        return ['cbc = "0.2.1"', 'aes = "0.9.2"']

    def codeblock(self):
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

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')
