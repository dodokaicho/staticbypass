import random
import string

class vfilesystem:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.allow = ''
        self.deny = ''
        if 'allow' in arguments:
            self.allow = arguments['allow']
        if 'deny' in arguments:
            self.deny = arguments['deny']
        else:
            self.deny = 'C:\\\\INTERNAL\\\\__empty'

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return f'{self.name}();\n\t' + shellcodestring

    def codeblock(self) -> str:
        if self.allow:
            allow = f'if (GetFileAttributesA("{self.allow}") == INVALID_FILE_ATTRIBUTES) exit(0);'
        else:
            allow = ''
        if self.deny:
            deny = f'if (GetFileAttributesA("{self.deny}") != INVALID_FILE_ATTRIBUTES) exit(0);'
        else:
            deny = ''

        return f"""
void {self.name}()
{{
    {allow}
    {deny}
}}
"""