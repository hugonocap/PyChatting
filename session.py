import socket

# Just constants
INBUFSIZE = 1024

# Session state

class SessionState:
    START  = 1
    LOGIN  = START
    CMD    = 2
    FINISH = 3
    ERROR  = 4

class SessionCmd:
    QUIT = 'quit'
    HELP = 'help'

class HandleReturn:
    FALSE = False
    TRUE  = True

class Session:
    def __init__(self, connection):
        self.sd   = connection[0]
        self.addr = connection[1]
        self.name = ''
        self.state = SessionState.START
        self.buf = ''
        self.send_msg('Enter your name: ')

    def __del__(self):
        self.sd.close()

    def get_sd(self):
        return self.sd

    def send_msg(self, msg):
        self.sd.sendall(msg.replace('\n', '\r\n').encode())

    def login(self, name):
        self.name = name
        self.send_msg(f'Welcome {name}!\n')

    def cmd(self, cmd):
        match cmd:
            case SessionCmd.QUIT:
                self.send_msg(f'Goodbye {self.name}!\n')
                self.state = SessionState.FINISH
            case SessionCmd.HELP:
                self.send_msg(f'\'{SessionCmd.QUIT}\' to quit server\n'
                              f'\'{SessionCmd.HELP}\' to get this help\n')
            case _:
                self.send_msg(f'Invalid command, try \'help\'\n')

    def handle(self):
        if not (buf := self.sd.recv(INBUFSIZE)):
            return HandleReturn.FALSE
        self.buf += buf.decode()

        buf, sep, self.buf = self.buf.partition('\r\n')
        if not sep:
            self.buf = buf
            return HandleReturn.TRUE

        match self.state:
            case SessionState.LOGIN:
                self.login(buf)
                self.state = SessionState.CMD
            case SessionState.CMD:
                self.cmd(buf)
            case _:
                pass

        return self.state != SessionState.FINISH and self.state != SessionState.ERROR
