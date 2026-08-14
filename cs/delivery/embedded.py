import random
import string
from utils.utils import *

class embedded:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = 'string'
        elif shellcodeType == "bytes":
            self.type = 'byte[]'
        elif shellcodeType == "list":
            self.type = 'string[]'
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_cs'](shellcode, 'obfuscated')

    def imports(self):
        return []

    def codeblock(self):
        
        return f"""

        public static {self.type} {self.name}()
        {{
            {self.shellcode}
            return obfuscated;
        }}

"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
