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
        while True:
            buf = self.sd.recv(INBUFSIZE)
            if not buf:
                break
            print(buf.decode(), end='', flush=True)
        self.sd.close()
        print('Server closed the connection, try ENTER to quit')

    def init_success(self):
        return self.sd.fileno() > -1

    def run(self):
        recv_thread = Thread(target=self.__handle_recv)
        recv_thread.start()

        while True:
            buf = input()
            try:
                self.sd.sendall(f'{buf}\r\n'.encode())
            except:
                break
