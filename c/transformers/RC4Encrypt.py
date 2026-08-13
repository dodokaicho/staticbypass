import os
from utils.utils import bytes_to_c
from Crypto.Cipher import ARC4
import string
import random

class RC4Encrypt:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def compilerOptions(self):
        return []

    def imports(self):
        return []

    def codeblock(self):
        return """
unsigned char * {name}(unsigned char * ciphertext){{

    {key}
    int N = 256;
    unsigned char S[256];
    unsigned char *plaintext = malloc({shellcodeSize});
    int keyLen = sizeof(key);
    int j = 0;
    int tmp = 0;

    for(int i = 0; i < N; i++){{
        S[i] = i;
    }}
        
    for(int i = 0; i < N; i++) {{
        j = (j + S[i] + key[i % keyLen]) % N;
        tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
    }}

    int i = 0;
    j = 0;

    for(size_t n = 0; n < {shellcodeSize}; n++) {{
        i = (i + 1) % N;
        j = (j + S[i]) % N;

        tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
        int rnd = S[(S[i] + S[j]) % N];

        plaintext[n] = rnd ^ ciphertext[n];
    }}

    return plaintext;
}}
""".format(name=self.name, key = bytes_to_c(self.key, 'key'), shellcodeSize=self.shellcodeSize)

    def encode(self, plaintext):
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')