def bytes_to_vba(bytestring: bytes, name: str) -> str:
    arrayString = f'\tDim {name}(0 To {len(bytestring) - 1}) As Byte\n'

    for i in range(0, len(bytestring)):
        arrayString += f'\t{name}({i}) = {bytestring[i]}\n'
    return arrayString

def str_to_vba(string: str, name: str) -> str:

    returnString = f'Dim {name} as String: {name} = '
    for i in range(0, len(string), 900):
        substring = string[i:i+900]
        if len(substring) < 900:
            returnString += f'"{substring}"\n'
        else:
            returnString += f'"{substring}" & _\n'

    return returnString

def list_to_vba(itemList: list[str], name: str) -> str:

    joinedString = ','.join(itemList)

    returnString = f'Dim {name}() as String: {name} = Split('
    for i in range(0, len(joinedString), 900):
        substring = joinedString[i:i+900]
        if len(substring) < 900:
            returnString += f'"{substring}",",")\n'
        else:
            returnString += f'"{substring}" & _\n'

    return returnString

def dict_to_vba(dictionary: dict[str, int], name: str) -> str:
    returnString = f"\tDim {name}\n"
    returnString += f"\tSet {name} = CreateObject(\"Scripting.Dictionary\")\n"
    returnString += '\n'.join([f'\t{name}.Add "{key}", {value}' for key, value in dictionary.items()]) 
    return returnString