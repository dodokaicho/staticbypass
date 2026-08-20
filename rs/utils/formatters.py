def bytes_to_rs(bytestring: bytes, name: str) -> str:
    # return f'let {name}= vec![{','.join([f'{hex(val)}' for val in bytestring])}];'
    return f'let {name}: [u8; {len(bytestring)}] = [{','.join([f'{hex(val)}' for val in bytestring])}];'

def str_to_rs(string: str, name: str) -> str:
    return f'let {name} = String::from("{string}");'

def list_to_rs(itemList: list[str], name: str) -> str:
    return f'let {name}: Vec<String> = vec![{','.join(f'"{s}"' for s in itemList)}].into_iter().map(|s| s.into()).collect();'
    #return f'let {name}: [&str; {len(itemList)}] = [{','.join(f'"{s}"' for s in itemList)}];'

def dict_to_rs(dictionary: dict[str, int], name: str) -> str:
    outString = f'let {name} = HashMap::from(['
    for key, value in dictionary.items():
        outString += f'("{key}", {value}),'
    outString += ']);\n'
    return outString