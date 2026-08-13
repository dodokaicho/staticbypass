import os
from utils.utils import bytes_to_ps1
from Crypto.Cipher import ARC4
import string
import random

class RC4Encrypt:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

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

        $ciphertext = $buffer.ToArray()

        {key}
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
""".format(name=self.name, key = bytes_to_ps1(self.key, 'Key'))

    def encode(self, plaintext):
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')