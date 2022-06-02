import socket

# Just constants
INBUFSIZE = 1024

# Session state

class SessionState:
    START  = 1
    LOGIN  = START
    FINISH = 2
    ERROR  = 3

class Session:
    def __init__(self, connection):
        self.sd   = connection[0]
        self.addr = connection[1]
        self.state = SessionState.START
        self.buf = ''
        self.send_msg('Welcome!\n'
                      'Enter your name: ')

    def __del__(self):
        self.sd.close()

    def send_msg(self, msg):
        self.sd.sendall(msg.replace('\n', '\r\n').encode())

    def login(self, buf):
        self.send_msg(f'Your name is {buf}, bye!\n')

    def handle(self):
        if not (buf := self.sd.recv(INBUFSIZE)):
            return False
        self.buf += buf.decode()

        buf, sep, self.buf = self.buf.partition('\r\n')
        if not sep:
            self.buf = buf
            return True

        match self.state:
            case SessionState.LOGIN:
                self.login(buf)
                self.state = SessionState.FINISH
            case _:
                pass

        return self.state != SessionState.FINISH and self.state != SessionState.ERROR
