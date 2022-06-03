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
    KICK   = '/kick'
    OWNER  = '/owner'

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
            self.state = SessionState.ERROR
            return False
        if len(self.buf) >= INBUFSIZE:
            self.state = SessionState.ERROR
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

    def __new_room(self, r, name='', password='nopass', max_count=5):
        if not name:
            name = f'{self.name}\'s room'
        t = room.Room(room.get_free_rid(r), self.name, name, password, max_count)
        r.append(t)
        self.__join_room(t, password)

    def __list_room(self, r):
        count = len(r)
        buf = f'{count} rooms are available:\n'
        for t in r:
            buf += f'\t{t.get_info()}\n'
        if count <= 0:
            buf += f'\tTry \'{SessionCmd.NEW}\' to make new room\n'
        self.send_msg(buf, True)

    def __join_room(self, r, password='nopass'):
        if not r.check_password(password):
            self.send_msg('Wrong password\n')
            return
        if not r.add_session(self):
            self.send_msg('Can\'t join the room...\n', True)
            return
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
                              f'\t\'{SessionCmd.NEW}\'  to make default room\n'
                              f'\t\'{SessionCmd.NEW}\'  [$name in \'quotes\'] '
                               '[$pass or nopass] [$max_count]\n'
                              f'\t\'{SessionCmd.LIST}\' to list all rooms\n'
                              f'\t\'{SessionCmd.JOIN}\' to join the room '
                               'without a password\n'
                              f'\t\'{SessionCmd.JOIN}\' [room id] '
                               '[optional $pass]\n'
                               '\n\tYou have to write room name in '
                               'quotes: (\' and \").\n'
                               '\tYou can also add backslash to add quote\n'
                               '\tin your room name like "\\"room\\"".\n',
                              True)
            case SessionCmd.NEW:
                name, args = partition_quotes(args)
                password, sep, max_count = args.partition(' ')
                try:
                    self.__new_room(r, name, password, int(max_count))
                except:
                    self.__new_room(r)
            case SessionCmd.LIST:
                self.__list_room(r)
            case SessionCmd.JOIN:
                try:
                    rid, sep, password = args.partition(' ')
                    if t := room.get_room_by_id(r, int(rid)):
                        if password:
                            self.__join_room(t, password)
                        else:
                            self.__join_room(t)
                    else:
                        self.send_msg('Wrong room id\n', True)
                except:
                    self.send_msg(f'Join usage: {SessionCmd.JOIN} [room id] '
                                   '[optional $pass]\n', True)
            case _:
                self.send_msg(f'Invalid command, try \'{SessionCmd.HELP}\'\n',
                              True)

    def __chat(self, buf, r):
        cmd, sep, args = buf.partition(' ')
        match cmd:
            case ChatCmd.QUIT:
                r.kick(self)
            case ChatCmd.HELP:
                self.send_msg('Available commands:\n'
                              f'\t\'{ChatCmd.QUIT}\'   to quit the room\n'
                              f'\t\'{ChatCmd.HELP}\'   to get this help\n'
                              f'\t\'{ChatCmd.ONLINE}\' to get users online\n'
                              f'\t\'{ChatCmd.KICK}\'   [name] [optional msg] '
                               'to kick user\n'
                              f'\t\'{ChatCmd.OWNER}\'  [name] to tranship '
                               'the owner\n',
                              True)
            case ChatCmd.ONLINE:
                self.send_msg(r.get_online(), True)
            case ChatCmd.KICK:
                if not args:
                    self.send_msg(f'Kick usage: {ChatCmd.KICK} [name] '
                                   '[optional msg]\n',
                                  True)
                    return
                name, sep, msg = args.partition(' ')
                if not r.owner_kick(self.name, name, msg):
                    self.send_msg(f'You can\'t kick\n', True)
            case ChatCmd.OWNER:
                if not args:
                    self.send_msg(f'Owner usage: {ChatCmd.OWNER} [name]\n', True)
                    return
                if not r.tranship_owner(self.name, args):
                    self.send_msg('You can\'t tranship the owner\n', True)
            case _:
                if buf and buf[0] != '/':
                    r.send_msg(f'\n>> {self.name}: {buf}\n', self)
                else:
                    self.send_msg(f'Invalid command, try \'{ChatCmd.HELP}\'\n',
                                  True)

def partition_quotes(str):
    if (len(str) < 2) or (str[0] not in ['\'', '"']):
        return (str, '')

    # Try to find quote from 1 position
    quote = str[0]
    start = 1
    while True:
        quote_pos = str.find(quote, start)
        if quote_pos == -1:
            return (str, '')
        if str[quote_pos-1] == '\\':
            start = quote_pos+1
        else:
            break

    # Try to get the rest of the string
    if quote_pos+2 < len(str):
        other = str[quote_pos+2:]
    else:
        other = ''

    return (str[1:quote_pos].replace('\\', ''), other)
