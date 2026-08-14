from utils.utils import bytes_to_c
from common.transformers.AESEncrypt import AESEncryptBase

class AESEncrypt(AESEncryptBase):

    def imports(self):
        return ["#include <bcrypt.h>", "#include <string.h>", "#pragma comment(lib, \"bcrypt.lib\")"]

    def compilerOptions(self):
        return ['-lbcrypt']

    def codeblock(self):
        return f"""

unsigned char *{self.name}(const unsigned char *ciphertext)
{{

    {bytes_to_c(self.key, 'key')}
    {bytes_to_c(self.iv, 'iv')}
    DWORD ciphertext_len = {self.ciphertextSize};
    DWORD key_len = sizeof(key);
    BCRYPT_ALG_HANDLE  hAlg       = NULL;
    BCRYPT_KEY_HANDLE  hKey       = NULL;
    PBYTE              pbKeyObj   = NULL;
    unsigned char     *iv_copy    = NULL;
    unsigned char     *plaintext  = NULL;
    DWORD              cbKeyObj   = 0, cbResult = 0, cbPlain = 0;
    NTSTATUS           status;

    /* ---- Open algorithm provider ---- */
    status = BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_AES_ALGORITHM, NULL, 0);
    if (!BCRYPT_SUCCESS(status)) goto cleanup;

    /* ---- Set CBC chaining mode ---- */
    status = BCryptSetProperty(hAlg,
                               BCRYPT_CHAINING_MODE,
                               (PBYTE)BCRYPT_CHAIN_MODE_CBC,
                               sizeof(BCRYPT_CHAIN_MODE_CBC), 0);
    if (!BCRYPT_SUCCESS(status)) goto cleanup;

    /* ---- Allocate key object buffer ---- */
    status = BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH,
                               (PBYTE)&cbKeyObj, sizeof(cbKeyObj),
                               &cbResult, 0);
    if (!BCRYPT_SUCCESS(status)) goto cleanup;

    pbKeyObj = (PBYTE)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, cbKeyObj);
    if (!pbKeyObj) goto cleanup;

    /* ---- Import symmetric key ---- */
    status = BCryptGenerateSymmetricKey(hAlg, &hKey,
                                        pbKeyObj, cbKeyObj,
                                        (PUCHAR)key, key_len, 0);
    if (!BCRYPT_SUCCESS(status)) goto cleanup;

    /* ---- Copy IV — BCryptDecrypt modifies the IV buffer in-place ---- */
    iv_copy = (unsigned char *)HeapAlloc(GetProcessHeap(), 0, 16);
    if (!iv_copy) goto cleanup;
    memcpy(iv_copy, iv, 16);

    /* ---- First call: get required output size ---- */
    status = BCryptDecrypt(hKey,
                           (PUCHAR)ciphertext, ciphertext_len,
                           NULL,
                           iv_copy, 16,
                           NULL, 0, &cbPlain,
                           BCRYPT_BLOCK_PADDING);
    if (!BCRYPT_SUCCESS(status)) goto cleanup;

    plaintext = (unsigned char *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, cbPlain);
    if (!plaintext) goto cleanup;

    /* ---- Reset IV copy, then decrypt ---- */
    memcpy(iv_copy, iv, 16);

    status = BCryptDecrypt(hKey,
                           (PUCHAR)ciphertext, ciphertext_len,
                           NULL,
                           iv_copy, 16,
                           plaintext, cbPlain, &cbPlain,
                           BCRYPT_BLOCK_PADDING);
    if (!BCRYPT_SUCCESS(status)) {{
        HeapFree(GetProcessHeap(), 0, plaintext);
        plaintext = NULL;
        goto cleanup;
    }}

cleanup:
    if (iv_copy)  HeapFree(GetProcessHeap(), 0, iv_copy);
    if (hKey)     BCryptDestroyKey(hKey);
    if (hAlg)     BCryptCloseAlgorithmProvider(hAlg, 0);
    if (pbKeyObj) HeapFree(GetProcessHeap(), 0, pbKeyObj);

    return plaintext;
}}
"""