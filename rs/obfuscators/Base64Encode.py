import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self):
        return ["use base64::prelude::*;"]

    def codeblock(self):
        return """

fn {name}(encoded: &str) -> Vec<u8> {{
    BASE64_STANDARD.decode(encoded).unwrap()
}}

""".format(name = self.name)

    def compilerOptions(self):
        return ['base64 = "0.22.1"']

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def obfuscate(self, decoded):
        return base64.b64encode(decoded).decode()
            