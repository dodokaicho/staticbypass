import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return ["using System.Text;"]
    
    def compilerOptions(self):
        return []

    def codeblock(self):
        return """

        public static byte[] {name}(string encoded)
        {{
            return Convert.FromBase64String(encoded);
        }}
""".format(name = self.name)

    def obfuscate(self, decoded):
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

            