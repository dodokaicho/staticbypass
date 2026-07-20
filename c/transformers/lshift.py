import os
import string
import random

class lshift:

    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def compilerOptions(self):
        return []

    def codeblock(self):
        return """

unsigned char *{name}(const unsigned char *encoded)
{{
    int len = {plaintextSize};
    unsigned char * decoded = malloc(len);
    for (int i=0; i<len; i++){{
        decoded[i] = (encoded[i] >> 4) | (encoded[i] << 4);
    }}
    return decoded;
}}
""".format(name=self.name, plaintextSize = self.plaintextSize)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def encode(self, plaintext):
        self.plaintextSize = len(plaintext)
        encoded = b''
        for i in range(len(plaintext)):
            encoded += (((plaintext[i] << 4) | (plaintext[i] >> 4)) & 255).to_bytes(1)
        return encoded
