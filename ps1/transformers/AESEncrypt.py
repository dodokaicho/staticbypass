from ps1.utils.formatters import bytes_to_ps1
import os
from Crypto.Cipher import AES
from Crypto.Util import Padding
import string
import random


class AESEncrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(32)
        if 'iv' in arguments:
            self.iv = arguments['iv'].encode()
        else:
            self.iv = os.urandom(16)

    def compilerOptions(self) -> list[str]:
        return []

    def imports(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        self.plaintextSize = len(plaintext)
        encrypted = cipher.encrypt(Padding.pad(plaintext, 16, style='pkcs7'))
        self.ciphertextSize = len(encrypted)
        return encrypted

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')

    def codeblock(self) -> str:
        return f"""
function {self.name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [byte[]]$CipherBytes,

        [System.Security.Cryptography.CipherMode]$Mode =
            [System.Security.Cryptography.CipherMode]::CBC,

        [System.Security.Cryptography.PaddingMode]$Padding =
            [System.Security.Cryptography.PaddingMode]::PKCS7
    )
    begin {{
        $buffer = [System.Collections.Generic.List[byte]]::new()
    }}
    process {{
        $buffer.AddRange($CipherBytes)
    }}
    end {{
        $cipher = $buffer.ToArray()
        {bytes_to_ps1(self.key, 'Key')}
        {bytes_to_ps1(self.iv, 'IV')}

        $aes = [System.Security.Cryptography.Aes]::Create()
        $aes.Key     = $Key
        $aes.Mode    = $Mode
        $aes.Padding = $Padding
        $aes.IV = $IV

        $decryptor = $aes.CreateDecryptor()
        return $decryptor.TransformFinalBlock($cipher, 0, {self.ciphertextSize})
    }}
}}
"""