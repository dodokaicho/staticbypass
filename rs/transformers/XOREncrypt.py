import random
import string
from utils.utils import bytes_to_rs
import os

class XOREncrypt:

    def __init__(self, arguments):
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self):
        return []
    
    def compilerOptions(self):
        return []

    def codeblock(self):
        return """
fn {name}(a: &[u8]) -> Vec<u8>{{
    {key}
    a.iter()
        .enumerate()
        .map(|(i, &byte)| byte ^ key[i % key.len()])
        .collect()
}}
""".format(name = self.name, key=bytes_to_rs(self.key, 'key'), ciphertextSize = self.ciphertextSize)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def encode(self, plaintext):
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))