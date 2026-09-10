from string import Template

class rundll:
    def __init__(self, arguments) -> None:
        with open('dllmain.c', 'w') as f:
            inline_assembly = """
#include <windows.h>

void OnProcessAttach();

DWORD WINAPI MyThreadFunction(LPVOID lpParam) {
    OnProcessAttach();
    return 0;
}

BOOL WINAPI DllMain(
    HINSTANCE _hinstDLL,  // handle to DLL module
    DWORD _fdwReason,     // reason for calling function
    LPVOID _lpReserved)   // reserved
{
    switch (_fdwReason) {
    case DLL_PROCESS_ATTACH:
		    // Initialize once for each new process.
        // Return FALSE to fail DLL load.
        {
            HANDLE hThread = CreateThread(NULL, 0, MyThreadFunction, 0, 0, NULL);
            // CreateThread() because otherwise DllMain() is highly likely to deadlock.
        }
        break;
    case DLL_PROCESS_DETACH:
        // Perform any necessary cleanup.
        break;
    case DLL_THREAD_DETACH:
        // Do thread-specific cleanup.
        break;
    case DLL_THREAD_ATTACH:
		// Do thread-specific initialization.
        break;
    }
    return TRUE; // Successful.
}
"""
            f.write(inline_assembly)

    def imports(self) -> list[str]:
        return ['golang.org/x/sys/windows']

    def compilerOptions(self) -> list[str]:
        return []

    def template(self) -> str:
        return """
package main

import "C"

import (
{imports}
)

{codeblocks}

func main() {{}}

//export OnProcessAttach
func OnProcessAttach() {{

    {template}
}}
"""