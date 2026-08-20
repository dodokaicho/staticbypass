import random
import string
from rs.utils.formatters import dict_to_rs
import time

class DictObfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
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
        return ['use std::collections::HashMap;']

    def compilerOptions(self):
        return []

    def codeblock(self):

        wordArray = dict_to_rs(self.dictdecode, 'wordarray')

        return f"""
fn {self.name}(encoded: &str) -> Vec<u8> {{
    {wordArray}
    let split: Vec<&str> = encoded.split(' ').collect();
    let mut decoded = vec![0; split.len()];
    for (i, word) in split.iter().enumerate(){{
        decoded[i] = wordarray.get(word).copied().unwrap();
    }}

    decoded
}}
"""

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')

    def obfuscate(self, decoded):
        self.size = len(decoded)
        encoded = ''
        for i in range(0, len(decoded) - 1):
            encoded += self.dictencode[decoded[i]] + ' '
        encoded += self.dictencode[decoded[-1]]
        return encoded