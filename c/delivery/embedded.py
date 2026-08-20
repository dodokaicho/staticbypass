import random
import string
from c.utils.formatters import *

class embedded:

    def __init__(self, shellcode: str | bytes | list[str], arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = 'const unsigned char *'
        elif shellcodeType == "bytes":
            self.type = 'const unsigned char *'
        elif shellcodeType == "list":
            self.type = 'const unsigned char **'
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_c'](shellcode, 'obfuscated')

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}()')

    def codeblock(self) -> str:
        return f"""
{self.type} {self.name}() {{
    {self.shellcode}
    return obfuscated;
}}
"""
