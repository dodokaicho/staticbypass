def bytes_to_go(bytestring: bytes, name: str) -> str:
    return f'{name}:= []byte{{ {','.join([hex(x) for x in bytestring])} }}'

def str_to_go(string: str, name: str) -> str:
    return f'{name}:= "{string}"'