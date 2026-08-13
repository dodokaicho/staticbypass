import random
import string
from utils.utils import bytes_to_c
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
unsigned char * {name}(const unsigned char * ciphertext)
{{
    {key}
    int length = {ciphertextSize};
    unsigned char* plaintext = malloc(length);
    for (int i=0; i<length; i++){{
        plaintext[i] = ciphertext[i] ^ key[i % sizeof(key)];
    }}
    return plaintext;
}}
""".format(name = self.name, key=bytes_to_c(self.key, 'key'), ciphertextSize = self.ciphertextSize)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def encode(self, plaintext):
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))