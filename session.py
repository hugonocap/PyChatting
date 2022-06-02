import socket

import room

INBUFSIZE = 1024

class SessionState:
    START    = 1
    LOGIN    = START
    CMD      = 2
    ROOM     = 6
    FINISH   = 3
    ERROR    = 4

class SessionCmd:
    QUIT = 'quit'
    HELP = 'help'
    NEW  = 'new'

class ChatCmd:
    QUIT = '/quit'
    HELP = '/help'

class HandleReturn:
    FALSE = 0
    TRUE  = 1

class Session:
    def __init__(self, connection):
        self.sd   = connection[0]
        self.addr = connection[1]
        self.name = ''
        self.room = -1
        self.state = SessionState.START
        self.buf = ''
        self.send_msg('Enter your name: ')

    def __del__(self):
        self.sd.close()

    def get_sd(self):
        return self.sd

    def get_room(self):
        return self.room

    def send_msg(self, msg):
        self.sd.sendall(msg.replace('\n', '\r\n').encode())

    def login(self, name):
        self.name = name
        self.send_msg(f'Welcome {name}!\n')

    def new_room(self, r):
        t = room.Room(room.get_free_rid(r), self)
        r.append(t)
        self.join_room(t)

    def cmd(self, cmd, r):
        match cmd:
            case SessionCmd.QUIT:
                self.send_msg(f'Goodbye {self.name}!\n')
                self.state = SessionState.FINISH
            case SessionCmd.HELP:
                self.send_msg('Sorry, this feature temporarily not implemented yet\n')
            case SessionCmd.NEW:
                self.new_room(r)
            case _:
                self.send_msg(f'Invalid command, try \'{SessionCmd.HELP}\'\n')

    def chat(self, buf, r):
        match buf:
            case ChatCmd.QUIT:
                self.leave_room()
            case ChatCmd.HELP:
                self.send_msg('Sorry, this feature temporarily not implemented yet\n')
            case _:
                if buf and buf[0] != '/':
                    r.send_msg(f'\n>> {self.name}: {buf}\n', self)
                else:
                    self.send_msg(f'Invalid command, try \'{ChatCmd.HELP}\'\n')

    def handle(self, r, self_r):
        if not (buf := self.sd.recv(INBUFSIZE)):
            self.state = SessionState.ERROR
            return HandleReturn.FALSE

        self.buf += buf.decode()
        if len(self.buf) >= INBUFSIZE:
            return HandleReturn.FALSE

        buf, sep, self.buf = self.buf.partition('\r\n')
        if not sep:
            self.buf = buf
            return HandleReturn.TRUE

        match self.state:
            case SessionState.LOGIN:
                self.login(buf)
                self.state = SessionState.CMD
            case SessionState.CMD:
                self.cmd(buf, r)
            case SessionState.ROOM:
                self.chat(buf, self_r)
            case _:
                pass

        match self.state:
            case SessionState.FINISH:
                return HandleReturn.FALSE
            case SessionState.ERROR:
                return HandleReturn.FALSE
            case _:
                return HandleReturn.TRUE

    def join_room(self, r):
        self.room = r.get_id()
        self.state = SessionState.ROOM
        r.add_session(self)

    def leave_room(self):
        self.room = -1
        self.state = SessionState.CMD
