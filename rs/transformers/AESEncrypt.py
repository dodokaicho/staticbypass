import os
from utils.utils import bytes_to_rs
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random

class AESEncrypt:

    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        self.key = os.urandom(32)
        self.iv = os.urandom(16)

    def imports(self):
        return ["extern crate openssl;", "use openssl::symm::{Cipher, Crypter, Mode};"]

    def compilerOptions(self):
        return ['openssl = {version = "0.10.81", features = ["vendored"]}']

    def codeblock(self):
        return """
fn {name}(encrypted_data: &[u8]) -> Vec<u8>{{
    {key}
    {iv}
    let cipher = Cipher::aes_256_cbc();
    let mut decrypter = Crypter::new(cipher, Mode::Decrypt, &key, Some(&iv)).unwrap();

    let block_size = cipher.block_size();
    let mut decrypted_data = vec![0; encrypted_data.len() + block_size];
    let count = decrypter
        .update(encrypted_data, &mut decrypted_data)
        .unwrap();
    let rest = decrypter.finalize(&mut decrypted_data[count..]).unwrap();
    decrypted_data.truncate(count + rest);

    decrypted_data
}}
""".format(name=self.name, key=bytes_to_rs(self.key, 'key'), iv=bytes_to_rs(self.iv, 'iv'), ciphertextSize = self.ciphertextSize)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def encode(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted
