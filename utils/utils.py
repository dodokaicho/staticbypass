import random

def bytes_to_cs(bytestring, name):
    return f'byte[] {name} = new byte [{len(bytestring)}] {{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_cs(string, name):
    return f'string {name} = "{string}";'
    
def list_to_cs(itemList, name):
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'string[] {name} = {{ {encodedString} }};'

def bytes_to_c(bytestring, name):
    return f'static const unsigned char {name}[] = ' + '{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_c(string, name):
    return f'static const unsigned char {name}[] = "{string}\\0";'

def list_to_c(itemList, name):
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'static const unsigned char *{name}[] = {{{encodedString}}};'

def bytes_to_vba(bytestring, name):
    arrayString = f'\tDim {name}(0 To {len(bytestring) - 1}) As Byte\n'

    for i in range(0, len(bytestring)):
        arrayString += f'\t{name}({i}) = {bytestring[i]}\n'
    return arrayString

def str_to_vba(string, name):

    returnString = f'Dim {name} as String: {name} = '
    for i in range(0, len(string), 900):
        substring = string[i:i+900]
        if len(substring) < 900:
            returnString += f'"{substring}"\n'
        else:
            returnString += f'"{substring}" & _\n'

    return returnString

def bytes_to_ps1(bytestring, name):
    return f'[Byte[]]${name} = {','.join([f'0x{bytestring[i]:02x}' for i in range(0, len(bytestring))])}'

def str_to_ps1(string, name):
    return f'[String]${name} = "{string}"'

def list_to_ps1(itemList, name):
    return f'${name} = @({','.join([f"'{x}'" for x in itemList])})'

def dict_to_ps1(dictionary, name):
    outString = f'${name} = @{{'
    outString += ';'.join([f'"{key}"={value}' for key, value in dictionary.items()])
    outString += '}'
    return outString

def list_to_vba(itemList, name):

    joinedString = ','.join(itemList)

    returnString = f'Dim {name}() as String: {name} = Split('
    for i in range(0, len(joinedString), 900):
        substring = joinedString[i:i+900]
        if len(substring) < 900:
            returnString += f'"{substring}",",")\n'
        else:
            returnString += f'"{substring}" & _\n'


    return returnString

def bytes_to_rs(bytestring, name):
    # return f'let {name}= vec![{','.join([f'{hex(val)}' for val in bytestring])}];'
    return f'let {name}: [u8; {len(bytestring)}] = [{','.join([f'{hex(val)}' for val in bytestring])}];'

def str_to_rs(string, name):
    return f'let {name} = String::from("{string}");'

def list_to_rs(itemList, name):
    return f'let {name}: [&str; {len(itemList)}] = [{','.join(f'"{s}"' for s in itemList)}];'

def dict_to_rs(dictionary, name):
    outString = f'let {name} = HashMap::from(['
    for key, value in dictionary.items():
        outString += f'("{key}", {value}),'
    outString += ']);\n'
    return outString

def generateFunctionName():
    return random.choice(open('wordlists/verbs.txt', 'r').readlines()).strip() + random.choice(open('wordlists/nouns.txt', 'r').readlines()).strip()