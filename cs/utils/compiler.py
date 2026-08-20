import subprocess
import platform

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if output[-4:] == '.exe':
        sourcefile = f'{output[:-4]}.cs'
        outfile = output
    else:
        sourcefile = f'{output}.cs'
        outfile = f'{output}.exe'
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    if platform.system() == 'Windows':
        result = subprocess.run(['C:\\windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe', sourcefile, f'-out:{outfile}'] + compilerOptions, check=True)
    elif platform.system() == 'Linux':
        result = subprocess.run(['mcs', sourcefile, f'-out:{outfile}'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile