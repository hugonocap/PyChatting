from sys import argv, stderr
from threading import Thread
import socket

INBUFSIZE = 1024

def handle_recv(client):
    while buf := client.recv(INBUFSIZE):
        print(buf.decode(), end='', flush=True)
    print('Server closed the connection, try ENTER to quit')

def main():
    try:
        ip, port = argv[1], int(argv[2])
    except:
        print('Usage: client [ip] [port]', file=stderr)
        quit(1)

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
    except socket.error as err:
        print(err, file=stderr)
        quit(1)

    recv_thread = Thread(target=handle_recv, args=[client])
    recv_thread.start()

    while buf := input():
        client.sendall(f'{buf}\r\n'.encode())
    client.close()
    quit()

main()
