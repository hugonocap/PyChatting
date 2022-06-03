def partition_quotes(str):
    if (len(str) < 2) or (str[0] not in ['\'', '"']):
        return (str, '')

    # Try to find quote from 1 position
    quote = str[0]
    start = 1
    while True:
        quote_pos = str.find(quote, start)
        if quote_pos == -1:
            return (str, '')
        if str[quote_pos-1] == '\\':
            start = quote_pos+1
        else:
            break

    # Try to get the rest of the string
    if quote_pos+2 < len(str):
        other = str[quote_pos+2:]
    else:
        other = ''

    return (str[1:quote_pos].replace('\\', ''), other)
