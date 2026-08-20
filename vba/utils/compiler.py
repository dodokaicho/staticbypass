from vba.utils.inject import create_word_doc

def compile(code: str, output: str, compilerOptions: list[str]) -> str:
    outfile = f'{output}.docm'
    open(f'{output}.vba', 'w').write(code)
    result = create_word_doc(code, outfile)
    print(f'Macro saved to {outfile}')
    return outfile