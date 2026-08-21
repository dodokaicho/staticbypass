
def bytes_to_cs(bytestring: bytes, name: str) -> str:
    return f'byte[] {name} = new byte [{len(bytestring)}] {{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_cs(string: str, name: str) -> str:
    return f'string {name} = "{string}";'
    
def list_to_cs(itemList: list[str], name: str) -> str:
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'string[] {name} = {{ {encodedString} }};'

def dict_to_cs(dictionary: dict[str, int], name: str) -> str:
    return f'var {name} = new Dictionary<string, byte> {{ {','.join([f'{{ "{key}", {value} }}' for key,value in dictionary.items()  ])} }};'