from utils.utils import bytes_to_cs

from common.transformers.AESEncrypt import AESEncryptBase

class AESEncrypt(AESEncryptBase):

    def __init__(self, arguments):
        super().__init__(arguments) 

    def imports(self):
        return ["using System.Security.Cryptography;"]

    def codeblock(self):
        return f"""
        public static byte[] {self.name}(byte[] ciphertext)
        {{
            byte[] plaintext;
            {bytes_to_cs(self.key, 'key')}
            {bytes_to_cs(self.iv, 'iv')}
            using (Aes aesAlg = Aes.Create())
            {{
                aesAlg.BlockSize = 128;
                aesAlg.KeySize = 128;
                aesAlg.Mode = CipherMode.CBC;
                aesAlg.Key = key;
                aesAlg.IV = iv;
                aesAlg.Padding = PaddingMode.PKCS7;  

                ICryptoTransform decryptor = aesAlg.CreateDecryptor(aesAlg.Key, aesAlg.IV);

                plaintext = decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
            }}
            return plaintext;
        }}
"""

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')