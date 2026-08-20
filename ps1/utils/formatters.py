def bytes_to_ps1(bytestring: bytes, name: str) -> str:
    return f'[Byte[]]${name} = {','.join([f'0x{bytestring[i]:02x}' for i in range(0, len(bytestring))])}'

def str_to_ps1(string: str, name: str) -> str:
    return f'[String]${name} = "{string}"'

def list_to_ps1(itemList: list[str], name: str) -> str:
    return f'${name} = @({','.join([f"'{x}'" for x in itemList])})'

def dict_to_ps1(dictionary: dict[str, int], name: str) -> str:
    outString = f'${name} = @{{'
    outString += ';'.join([f'"{key}"={value}' for key, value in dictionary.items()])
    outString += '}'
    return outString