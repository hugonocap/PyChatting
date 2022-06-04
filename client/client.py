import socket
from sys import stderr
from threading import Thread

INBUFSIZE = 1024

class Client:
    def __init__(self, addr):
        try:
            self.sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sd.connect(addr)
        except socket.error as err:
            print(err, file=stderr)
            quit(1)

    def __handle_recv(self):
        while buf := self.sd.recv(INBUFSIZE):
            print(buf.decode(), end='', flush=True)
        print('Server closed the connection, try ENTER to quit')

    def init_success(self):
        return self.sd.fileno() > -1

    def run(self):
        recv_thread = Thread(target=self.__handle_recv)
        recv_thread.start()

        while buf := input():
            self.sd.sendall(f'{buf}\r\n'.encode())
        self.sd.close()
