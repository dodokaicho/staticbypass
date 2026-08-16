import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
        public static byte[] {name}(string[] encoded)
        {{
            byte[] decoded = new byte[encoded.Length*16];
            for (int i=0; i<encoded.Length; i++){{
                string[] octets = encoded[i].Split(new [] {{':'}});
                for (int j=0; j < 8; j += 1){{
                    decoded[i*16+j*2] = (byte)Convert.ToInt32(octets[j].Substring(0, 2), 16);
                    decoded[i*16+j*2+1] = (byte)Convert.ToInt32(octets[j].Substring(2, 2), 16);
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
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')