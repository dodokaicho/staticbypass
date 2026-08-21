import random
import string
from go.utils.formatters import bytes_to_go
import os

class XOREncrypt:

    def __init__(self, arguments: dict) -> None:
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self) -> list[str]:
        return []
    
    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.ciphertextSize = len(plaintext)
        return bytes(plaintext[i] ^ self.key[i % len(self.key)] for i in range(0, len(plaintext)))

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
func {self.name}(ciphertext []byte) []byte {{
    {bytes_to_go(self.key, 'key')}
	plaintext := make([]byte, len(ciphertext))
	for i := 0; i < len(ciphertext); i++ {{
		plaintext[i] = ciphertext[i] ^ key[i%len(key)]
	}}
	return plaintext
}}
"""