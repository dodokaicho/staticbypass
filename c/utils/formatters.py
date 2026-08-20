def bytes_to_c(bytestring, name):
    return f'static const unsigned char {name}[] = ' + '{' + ','.join([f'{hex(val)}' for val in bytestring]) + '};'

def str_to_c(string, name):
    return f'static const unsigned char {name}[] = "{string}\\0";'

def list_to_c(itemList, name):
    encodedString = ",".join([f'"{x}"' for x in itemList])
    return f'static const unsigned char *{name}[] = {{{encodedString}}};'