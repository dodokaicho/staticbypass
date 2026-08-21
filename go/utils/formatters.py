def bytes_to_go(bytestring: bytes, name: str) -> str:
    return f'{name}:= []byte{{ {','.join([hex(x) for x in bytestring])} }}'

def str_to_go(string: str, name: str) -> str:
    return f'{name}:= "{string}"'

def list_to_go(itemList: list[str], name: str) -> str:
    return f'{name} := []string{{ {','.join([f'"{x}"' for x in itemList])} }}'

def dict_to_go(dictionary: dict[str, int], name: str) -> str:
    return f'{name} := map[string]int{{ {','.join([f'"{key}": {value}' for key,value in dictionary.items() ])}, }}'