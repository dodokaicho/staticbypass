import os
from Crypto.Cipher import ARC4
import string
import random
from cs.utils.formatters import bytes_to_cs

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

    def encode(self, plaintext):
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self):
        return f"""
    public static byte[] {self.name}(byte[] data)
    {{
        {bytes_to_cs(self.key, 'key')}
        byte[] S = new byte[256];
        byte[] T = new byte[256];

        for (int i = 0; i < 256; i++)
        {{
            S[i] = (byte)i;
            T[i] = key[i % key.Length];
        }}

        int j = 0;
        for (int i = 0; i < 256; i++)
        {{
            j = (j + S[i] + T[i]) % 256;
            byte temp = S[i];
            S[i] = S[j];
            S[j] = temp;
        }}

        int iIndex = 0;
        j = 0;
        byte[] result = new byte[data.Length];

        for (int k = 0; k < data.Length; k++)
        {{
            iIndex = (iIndex + 1) % 256;
            j = (j + S[iIndex]) % 256;

            byte temp = S[iIndex];
            S[iIndex] = S[j];
            S[j] = temp;

            byte keyStreamByte = S[(S[iIndex] + S[j]) % 256];
            result[k] = (byte)(data[k] ^ keyStreamByte);
        }}

        return result;
    }}"""

