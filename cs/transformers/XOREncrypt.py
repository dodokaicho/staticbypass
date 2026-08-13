import random
import string
from utils.utils import bytes_to_cs
import os
from itertools import cycle

class XOREncrypt:

    def __init__(self, arguments):
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def compilerOptions(self):
        return []

    def imports(self):
        return []

    def codeblock(self):
        return """
        public static byte[] {name}(byte[] ciphertext)
        {{
            {key}
            byte[] plaintext = new byte[ciphertext.Length];
            for (int i=0; i<ciphertext.Length; i++){{
                plaintext[i] = (byte)(ciphertext[i] ^ key[i % key.Length]);
            }}
            return plaintext;
        }}
""".format(name = self.name, key=bytes_to_cs(self.key, 'key'))

    def encode(self, plaintext):
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')