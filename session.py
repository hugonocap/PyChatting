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
    LIST = 'list'
    JOIN = 'join'

class ChatCmd:
    QUIT   = '/quit'
    HELP   = '/help'
    ONLINE = '/online'

class Session:
    def __init__(self, connection):
        self.sd   = connection[0]
        self.addr = connection[1]
        self.name = ''
        self.room = -1
        self.state = SessionState.START
        self.buf = ''
        self.send_msg('Enter your name: ', True)

    def __del__(self):
        self.sd.close()

    def get_sd(self):
        return self.sd

    def get_name(self):
        return self.name

    def get_room(self):
        return self.room

    def send_msg(self, msg, prefix=False):
        if prefix:
            msg = '> ' + msg
        self.sd.sendall(msg.replace('\n', '\r\n').encode())

    def handle(self, r, self_r):
        if not (buf := self.sd.recv(INBUFSIZE)):
            self.state = SessionState.ERROR
            return False

        try:
            self.buf += buf.decode()
        except:
            return False
        if len(self.buf) >= INBUFSIZE:
            return False

        buf, sep, self.buf = self.buf.partition('\r\n')
        if not sep:
            self.buf = buf
            return True

        match self.state:
            case SessionState.LOGIN:
                self.__login(buf)
                self.state = SessionState.CMD
            case SessionState.CMD:
                self.__cmd(buf, r)
            case SessionState.ROOM:
                self.__chat(buf, self_r)
            case _:
                pass

        return self.state != SessionState.FINISH and \
               self.state != SessionState.ERROR

    def __login(self, name):
        self.name = name
        self.send_msg(f'Welcome {name}! Try \'{SessionCmd.HELP}\' to '
                       'list the available commands\n', True)

    def __new_room(self, r):
        t = room.Room(room.get_free_rid(r), self.name)
        r.append(t)
        self.__join_room(t)

    def __list_room(self, r):
        count = len(r)
        buf = f'{count} rooms are available:\n'
        for t in r:
            buf += f'[{t.get_id()}] {t.get_name()} ' + \
                   f'({t.count()}/{t.get_max_count()})\n'
        if count <= 0:
            buf += f'\tTry \'{SessionCmd.NEW}\' to make new room\n'
        self.send_msg(buf, True)

    def __join_room(self, r):
        if not r.add_session(self):
            self.send_msg('Can\'t join the room...\n', True)
        self.room = r.get_id()
        self.state = SessionState.ROOM
        self.send_msg(f'You have joined the room with {self.room} id. '
                      f'Try \'{ChatCmd.HELP}\' to get available commands\n',
                      True)

    def leave_room(self):
        self.room = -1
        self.state = SessionState.CMD
        self.send_msg('You have left the room\n', True)

    def __cmd(self, cmd, r):
        cmd, sep, args = cmd.partition(' ')
        match cmd:
            case SessionCmd.QUIT:
                self.send_msg(f'Goodbye {self.name}!\n', True)
                self.state = SessionState.FINISH
            case SessionCmd.HELP:
                self.send_msg('Available commands:\n'
                              f'\t\'{SessionCmd.QUIT}\' to quit the server\n'
                              f'\t\'{SessionCmd.HELP}\' to get this help\n'
                              f'\t\'{SessionCmd.NEW}\'  to make new room\n'
                              f'\t\'{SessionCmd.LIST}\' to list all rooms\n'
                              f'\t\'{SessionCmd.JOIN}\' to join the room\n',
                              True)
            case SessionCmd.NEW:
                self.__new_room(r)
            case SessionCmd.LIST:
                self.__list_room(r)
            case SessionCmd.JOIN:
                try:
                    rid = int(args)
                    if t := room.get_room_by_id(r, rid):
                        self.__join_room(t)
                    else:
                        self.send_msg('Wrong room id\n', True)
                except:
                    self.send_msg('Join usage: join [room_id]\n', True)
            case _:
                self.send_msg(f'Invalid command, try \'{SessionCmd.HELP}\'\n',
                              True)

    def __chat(self, buf, r):
        match buf:
            case ChatCmd.QUIT:
                self.leave_room()
            case ChatCmd.HELP:
                self.send_msg('Available commands:\n'
                              f'\t\'{ChatCmd.QUIT}\'   to quit the room\n'
                              f'\t\'{ChatCmd.HELP}\'   to get this help\n'
                              f'\t\'{ChatCmd.ONLINE}\' to get users online\n',
                              True)
            case ChatCmd.ONLINE:
                self.send_msg(r.get_online(), True)
            case _:
                if buf and buf[0] != '/':
                    r.send_msg(f'\n>> {self.name}: {buf}\n', self)
                else:
                    self.send_msg(f'Invalid command, try \'{ChatCmd.HELP}\'\n',
                                  True)
