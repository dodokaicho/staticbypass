import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []
    
    def compilerOptions(self):
        return []

    def codeblock(self):
        return """
function {name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Encoded
    )
    process {{
        [byte[]]$bytes = [System.Convert]::FromBase64String($Encoded)
        return $bytes
    }}
}}
""".format(name = self.name)

    def obfuscate(self, decoded):
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')

            