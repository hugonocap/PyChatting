from sys import argv, stderr

import client

def main():
    try:
        ip, port = argv[1], int(argv[2])
    except:
        print('Usage: client [ip] [port]', file=stderr)
        quit(1)

    c = client.Client((ip, port))
    if not c.init_success():
        quit(1)
    c.run()

    quit()

main()
