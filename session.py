import socket

INBUFSIZE = 1024

class Session:
    def __init__(self, connection):
        self.sd = connection[0]
        self.addr = connection[1]

    def __del__(self):
        self.sd.close()

    def handle(self):
        if data := self.sd.recv(INBUFSIZE):
            self.sd.sendall(data)
            return True
        return False
