def bytes_to_pas(bytestring: bytes, name: str) -> str:
    #return f'{name}:array[0..{len(bytestring)}] of BYTE = ({','.join([f"${x:x}" for x in bytestring])});'
    return f'{name} := ArrBytes.Create({','.join([f"${x:x}" for x in bytestring])});'