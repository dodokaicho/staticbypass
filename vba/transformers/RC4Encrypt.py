from utils.utils import bytes_to_vba
from common.transformers.RC4Encrypt import RC4EncryptBase

class RC4Encrypt(RC4EncryptBase):

    def codeblock(self):
        return f"""
Function {self.name}(ciphertext() As Byte) As Byte()
    {bytes_to_vba(self.key, 'key')}
    Dim S(0 To 255) As Byte
    Dim i As Long, j As Long, k As Long, t As Byte, n As Long
    Dim keyLen As Long, cipherLen As Long
    Dim outBytes() As Byte

    keyLen = UBound(key) - LBound(key) + 1

    ' --- Key Scheduling Algorithm (KSA) ---
    For i = 0 To 255
        S(i) = i
    Next i

    j = 0
    For i = 0 To 255
        j = (j + S(i) + key(LBound(key) + (i Mod keyLen))) Mod 256
        t = S(i): S(i) = S(j): S(j) = t     ' swap
    Next i

    ' --- Pseudo-Random Generation Algorithm (PRGA) ---
    cipherLen = UBound(ciphertext) - LBound(ciphertext) + 1
    ReDim outBytes(0 To cipherLen - 1)

    i = 0: j = 0
    For n = 0 To cipherLen - 1
        i = (i + 1) Mod 256
        j = (j + S(i)) Mod 256
        t = S(i): S(i) = S(j): S(j) = t     ' swap
        k = S((CLng(S(i)) + CLng(S(j))) Mod 256)
        outBytes(n) = ciphertext(LBound(ciphertext) + n) Xor k
    Next n

    {self.name} = outBytes
End Function
"""