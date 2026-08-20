import os
from Crypto.Cipher import ARC4
from c.utils.formatters import bytes_to_c
import string
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def compilerOptions(self) -> list[str]:
        return []

    def imports(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
unsigned char * {self.name}(unsigned char * ciphertext){{

    {bytes_to_c(self.key, 'key')}
    int N = 256;
    unsigned char S[256];
    unsigned char *plaintext = malloc({self.shellcodeSize});
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

    for(size_t n = 0; n < {self.shellcodeSize}; n++) {{
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
"""
