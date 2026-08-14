import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return ["#include <stdio.h>", "#include <wincrypt.h>", "#include <stdlib.h>"]

    def codeblock(self):
        return """

unsigned char* {name}(const unsigned char* base64Str) {{

    // 1. Calculate the required buffer size
    DWORD binaryLen = 0;
    CryptStringToBinaryA(base64Str, 0, CRYPT_STRING_BASE64, 
                         NULL, &binaryLen, NULL, NULL);

    if (binaryLen == 0) return NULL;

    // 2. Allocate memory + 1 byte for null terminator
    char* decodedData = (char*)malloc(binaryLen + 1);
    if (decodedData == NULL) return NULL;

    // 3. Perform the actual decoding
    if (!CryptStringToBinaryA(base64Str, 0, CRYPT_STRING_BASE64, 
                             (BYTE*)decodedData, &binaryLen, NULL, NULL)) {{
        free(decodedData);
        return NULL;
    }}

    // 4. Null-terminate as a C-string
    decodedData[binaryLen] = '\\0';

    return decodedData;
}}

""".format(name = self.name)

    def compilerOptions(self):
        return ['-lcrypt32']

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def obfuscate(self, decoded):
        return base64.b64encode(decoded).decode()
            