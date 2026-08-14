import random
import string

class Whitespace:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
unsigned char * {name}(const unsigned char *encoded)
{{
    int size = {size};
    unsigned char *out = calloc(size, sizeof(unsigned char));
    for (int i=0; i < size; i++){{
        for (int j=0; j < 8; j++){{
            if (encoded[i*8 + j] == '\\t'){{
                out[i] += 1 << (7 - j);
            }}
        }}
    }}

    return out;
}}
""".format(name = self.name, size = self.size)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        self.size = len(decoded)
        binary = ''.join([f'{num:08b}' for num in decoded])
        binary = binary.replace('0', ' ')
        binary = binary.replace('1', '\t')
        return binary

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')