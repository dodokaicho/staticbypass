def bytes_to_go(bytestring: bytes, name: str) -> str:
    return f'{name}:= [{len(bytestring)}]byte{{ {','.join([hex(x) for x in bytestring])} }}'
