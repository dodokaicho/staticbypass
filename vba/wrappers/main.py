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
{imports}

{codeblocks}

Sub Document_Open()
    Main
End Sub

Sub AutoOpen()
    Main
End Sub

Sub Main()
    {template}
End Sub
"""