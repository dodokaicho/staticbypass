import base64
import random
import string


class Base64Encode:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []
    
    def compilerOptions(self) -> list[str]:
        return []

    def obfuscate(self, decoded: bytes) -> str:
        return base64.b64encode(decoded).decode()

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
Private Function {self.name}(strData)
    Dim i, inCount, outCount, firstTime
    Dim inArray(0 To 3) As Integer
    Dim outArray() As Byte

    Dim haystack
    haystack = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    firstTime = True
    While Len(strData) > 0

        inCount = 0
        For i = 1 To 4
            If Mid(strData, i, 1) <> "=" Then
                inArray(i - 1) = InStr(1, haystack, Mid(strData, i, 1), vbBinaryCompare) - 1
                inCount = inCount + 1
            Else
                Exit For
            End If
        Next

        outCount = inCount - 1
        If firstTime Then
            ReDim outArray(outCount - 1)
            firstTime = False
        Else
            ReDim Preserve outArray(UBound(outArray) + outCount)
        End If

        outArray(UBound(outArray) + 1 - outCount) = (inArray(0) And &H3F) * 4 + (inArray(1) And &H30) / 16
        If outCount >= 2 Then
            outArray(UBound(outArray) + 2 - outCount) = (inArray(1) And &HF) * 16 + (inArray(2) And &H3C) / 4
        End If
        If outCount >= 3 Then
            outArray(UBound(outArray) + 3 - outCount) = (inArray(2) And &H3) * 64 + (inArray(3) And &H3F)
        End If

        strData = Mid(strData, 5)
    Wend

    {self.name} = outArray
End Function
"""            