import codecs

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    if output[-4:] == '.ps1':
        outfile = output
    else:
        outfile = f'{output}.ps1'
    print(f'Writing source code to {outfile}')
    codecs.open(outfile, 'w', 'utf-8-sig').write(code)
    return outfile