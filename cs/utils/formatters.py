
def bytes_to_cs(bytestring, name):
    return f'byte[] {name} = new byte [{len(bytestring)}] {{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_cs(string, name):
    return f'string {name} = "{string}";'
    
def list_to_cs(itemList, name):
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'string[] {name} = {{ {encodedString} }};'