from sys import argv, stderr

import server

def main():
    try:
        ip = argv[1]
        port = int(argv[2])
    except:
        print('Error. Usage: serv [ip] [port]', file=stderr)
        quit(1)


    serv = server.Server(ip, port)
    if not serv.init_success():
        quit(1)
    serv.run()
    del serv

    quit()

main()
