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

        return """
function {name} {{
    [CmdletBinding()]
    [OutputType([byte[]])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Encoded
    )
    process {{
        {dictionary}

        $words = $Encoded -split " " 
        [byte[]]$bytes = [System.Array]::CreateInstance([byte],$words.Length)
        
        for (($i = 0); $i -lt $words.Length; $i++)
        {{
            $bytes[$i] = $dictionary[$words[$i]]
        }}

        return $bytes

    }}
}}
""".format(name = self.name, dictionary=dict_to_ps1(self.dictdecode, 'dictionary'))

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{{shellcode}} | {self.name}')

    def obfuscate(self, decoded):
        encoded = ''
        for i in range(0, len(decoded) - 1):
            encoded += self.dictencode[decoded[i]] + ' '
        encoded += self.dictencode[decoded[-1]]
        return encoded