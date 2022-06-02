from sys import argv

import server

def main():
    if len(argv) < 3:
        print('Error. Usage: serv [ip] [port]', file=sys.stderr)
        quit(1)

    if not (serv := server.Server(argv[1], int(argv[2]))):
        quit(1)
    serv.run()
    del serv

    quit()

main()
