def bytes_to_rs(bytestring, name):
    # return f'let {name}= vec![{','.join([f'{hex(val)}' for val in bytestring])}];'
    return f'let {name}: [u8; {len(bytestring)}] = [{','.join([f'{hex(val)}' for val in bytestring])}];'

def str_to_rs(string, name):
    return f'let {name} = String::from("{string}");'

def list_to_rs(itemList, name):
    return f'let {name}: Vec<String> = vec![{','.join(f'"{s}"' for s in itemList)}].into_iter().map(|s| s.into()).collect();'
    #return f'let {name}: [&str; {len(itemList)}] = [{','.join(f'"{s}"' for s in itemList)}];'

def dict_to_rs(dictionary, name):
    outString = f'let {name} = HashMap::from(['
    for key, value in dictionary.items():
        outString += f'("{key}", {value}),'
    outString += ']);\n'
    return outString