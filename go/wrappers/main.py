from string import Template

class main:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return []

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
package main

import (
{imports}
)

{codeblocks}

func main() {{

    {template}

}}
"""