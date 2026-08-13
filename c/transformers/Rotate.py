import os
import string
import random

class Rotate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'bits' in arguments:
            self.bits = int(arguments['bits'])
        else:
            self.bits = 4

    def imports(self):
        return []

    def compilerOptions(self):
        return []

    def codeblock(self):
        return f"""

unsigned char *{self.name}(const unsigned char *encoded)
{{
    int len = {self.plaintextSize};
    unsigned char * decoded = malloc(len);
    for (int i=0; i<len; i++){{
        decoded[i] = (encoded[i] >> {self.bits}) | (encoded[i] << {8 - self.bits});
    }}
    return decoded;
}}
"""

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def encode(self, plaintext):
        self.plaintextSize = len(plaintext)
        encoded = b''
        for i in range(len(plaintext)):
            encoded += ((plaintext[i] << (self.bits) | (plaintext[i] >> (8 - self.bits))) & 255).to_bytes(1)
        return encoded
