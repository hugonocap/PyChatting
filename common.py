def partition_quotes(str):
    if (len(str) < 2) or (str[0] not in ['\'', '"']):
        return (str, '')

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

    return (str[1:quote_pos].replace('\\', ''), str[quote_pos+2:])
