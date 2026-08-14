import random
import string
from utils.utils import list_to_c
import time

class DictObfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))
        if 'seed' in arguments:
            self.rng = random.Random(arguments['seed'])
        else:
            self.rng = random.Random(time.time())
        self.dictencode = {}
        self.dictdecode = []
        wordlist = open('wordlists/english.txt', 'r').readlines()
        randomNumbers = self.rng.sample(range(0, len(wordlist)), 256)
        for i in range(0, 256):
            word = wordlist[randomNumbers[i]].strip()
            self.dictencode[i] = word
            self.dictdecode.append({word: i})


    def imports(self):
        return ["#include <string.h>"]

    def compilerOptions(self):
        return []

    def codeblock(self):

        wordArray = list_to_c([self.dictencode[i] for i in range(0, 256)], 'wordArray')

        return """
unsigned char * {name}(const unsigned char* encoded)
{{
    int size = {size};
    unsigned char *buffer = strdup(encoded);
    unsigned char * out = malloc(size);
    int i = 0;
    {wordArray}
    char * currWord = strtok(buffer, " ");
    while (currWord != NULL){{
        for (int j = 0; j < 256; j++){{
            if (!strcmp(currWord, wordArray[j])){{
                out[i] = j;
            }}
        }}
        i++;
        currWord = strtok(NULL, " ");
    }}

    return out;
}}
""".format(name = self.name, wordArray=wordArray, size=self.size)

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def obfuscate(self, decoded):
        self.size = len(decoded)
        encoded = ''
        for i in range(0, len(decoded) - 1):
            encoded += self.dictencode[decoded[i]] + ' '
        encoded += self.dictencode[decoded[-1]]
        return encoded