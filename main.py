import sys

import server

def main():
    if len(sys.argv) < 3:
        print('Error. Usage: serv [ip] [port]', file=sys.stderr)
        quit(1)

    if not (serv := server.Server(sys.argv[1], int(sys.argv[2]))):
        quit(1)
    serv.run()
    del serv

    quit()

main()
