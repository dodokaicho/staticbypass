import random
import string
from uuid import UUID

class EmojiEncode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return ["#include <stdint.h>"]

    def compilerOptions(self):
        return []

    def codeblock(self):
        return """
unsigned char * {name}(const unsigned char *encoded)
{{
    int length = strlen(encoded);
    unsigned char *out = malloc(length/4);
    int hexcode;
    for (int i=0; i< length/4; i++ ){{
        unsigned char s[4];
        memcpy(s, &encoded[i*4], 4);
        hexcode = ((uint32_t)(s[0] & 0x07) << 18) | ((uint32_t)(s[1] & 0x3F) << 12) | ((uint32_t)(s[2] & 0x3F) << 6) |  (s[3] & 0x3F);
        out[i] = hexcode & 255;
    }}
    return out;
}}
""".format(name = self.name)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def obfuscate(self, decoded):
        encoded = ""
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded
