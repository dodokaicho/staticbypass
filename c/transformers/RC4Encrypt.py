from common.transformers.RC4Encrypt import RC4EncryptBase
from utils.utils import bytes_to_c

class RC4Encrypt(RC4EncryptBase):

    def codeblock(self):
        return f"""
unsigned char * {self.name}(unsigned char * ciphertext){{

    {bytes_to_c(self.key, 'key')}
    int N = 256;
    unsigned char S[256];
    unsigned char *plaintext = malloc({self.shellcodeSize});
    int keyLen = sizeof(key);
    int j = 0;
    int tmp = 0;

    for(int i = 0; i < N; i++){{
        S[i] = i;
    }}
        
    for(int i = 0; i < N; i++) {{
        j = (j + S[i] + key[i % keyLen]) % N;
        tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
    }}

    int i = 0;
    j = 0;

    for(size_t n = 0; n < {self.shellcodeSize}; n++) {{
        i = (i + 1) % N;
        j = (j + S[i]) % N;

        tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;
        int rnd = S[(S[i] + S[j]) % N];

        plaintext[n] = rnd ^ ciphertext[n];
    }}

    return plaintext;
}}
"""
