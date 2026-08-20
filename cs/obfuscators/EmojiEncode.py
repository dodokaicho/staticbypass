import random
import string

class EmojiEncode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def compilerOptions(self):
        return []

    def codeblock(self):
        return """
        public static byte[] {name}(string encoded)
        {{
            byte[] decoded = new byte[encoded.Length/2];
            for (int i=0; i< encoded.Length/2; i++ ){{
                decoded[i] = (byte)(char.ConvertToUtf32(encoded.Substring(i*2, 2), 0) & 255);
            }}
            return decoded;
        }}
""".format(name = self.name)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def obfuscate(self, decoded):
        encoded = ""
        for i in range(0, len(decoded)):
            encoded += chr(0x1f400 + decoded[i])
        return encoded
