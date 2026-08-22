def bytes_to_pas(bytestring: bytes, name: str) -> str:
    return f'{name} := TBytes.Create({','.join([f"${x:x}" for x in bytestring])});'