def bytes_to_ts(bytestring: bytes, name: str) -> str:
    return f'let {name}: Uint8Array = new Uint8Array([{ ','.join([hex(x) for x in bytestring]) }]);'

def str_to_ts(string: str, name: str,) -> str:
    return f'let {name}: string = "{string}";'

def list_to_ts(itemList: list[str], name: str) -> str:
    return f'let {name}: string[] = [ {','.join([f'"{x}"' for x in itemList])}  ];'

def dict_to_ts(dictionary: dict[str, int], name: str) -> str:
    return f'let {name}: Record<string, number> = {{ {','.join([f'"{key}": {value}' for key, value in dictionary.items()])} }};'