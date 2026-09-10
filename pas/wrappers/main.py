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
program output;

{{$codepage UTF8}}
{{$mode delphi}}

uses {imports};

{codeblocks}

{template}

begin
    main;
end.
"""