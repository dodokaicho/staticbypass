import random
import string
from utils.utils import bytes_to_ps1
import os
from itertools import cycle

class XOREncrypt:

    def __init__(self, arguments):
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def compilerOptions(self):
        return []

    def imports(self):
        return []

    def codeblock(self):
        return """
function {name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [byte[]]$CipherBytes
    )
    begin {{
        $buffer = [System.Collections.Generic.List[byte]]::new()
    }}
    process {{
        $buffer.AddRange($CipherBytes)
    }}
    end {{
        {key}
        $cipher = $buffer.ToArray()
        $output = [byte[]]::new($cipher.Length)
        for ($i = 0; $i -lt $cipher.Length; $i++) {{
            $output[$i] = $cipher[$i] -bxor $Key[$i % $Key.Length]
        }}
        return $output
    }}
}}
""".format(name = self.name, key=bytes_to_ps1(self.key, 'Key'))

    def encode(self, plaintext):
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')