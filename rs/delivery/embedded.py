import random
import string
from utils.utils import *

class embedded:

    def __init__(self, shellcode):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = 'String'
        elif shellcodeType == "bytes":
            self.type = f"[u8; {len(shellcode)}]"
        elif shellcodeType == "list":
            self.type = f"[&'static str; {len(shellcode)}]"
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_rs'](shellcode, 'obfuscated')

    def imports(self):
        return []

    def codeblock(self):
        
        return f"""

fn {self.name}() -> {self.type} {{
    {self.shellcode}
    return obfuscated;
}}
"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
