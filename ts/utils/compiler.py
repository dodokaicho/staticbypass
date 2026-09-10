import subprocess

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    filename = output.rsplit('.', 2)[0]
    sourcefile = f'{filename}.ts'
    outfile = f'{filename}.exe'
    print(f'Writing source code to {sourcefile}')
    open(sourcefile,'w').write(code)
    result = subprocess.run(['bun', 'build', sourcefile, '--compile', '--outfile', outfile, '--target=bun-windows-x64'] + compilerOptions, check=True)
    if result.returncode == 0:
        print(f'Payload saved to {outfile}')
    return outfile