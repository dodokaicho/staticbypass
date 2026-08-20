import random

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
    return f'let {name}: Vec<String> = vec![{','.join(f'"{s}"' for s in itemList)}].into_iter().map(|s| s.into()).collect();'
    #return f'let {name}: [&str; {len(itemList)}] = [{','.join(f'"{s}"' for s in itemList)}];'

def dict_to_rs(dictionary, name):
    outString = f'let {name} = HashMap::from(['
    for key, value in dictionary.items():
        outString += f'("{key}", {value}),'
    outString += ']);\n'
    return outString

def generateFunctionName():
    return random.choice(open('wordlists/verbs.txt', 'r').readlines()).strip() + random.choice(open('wordlists/nouns.txt', 'r').readlines()).strip()