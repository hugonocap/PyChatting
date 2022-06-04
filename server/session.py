import socket

from common import *
import room

INBUFSIZE = 1024

class SessionState:
    START    = 1
    LOGIN    = START
    CMD      = 2
    ROOM     = 3
    FINISH   = 4
    ERROR    = 5

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
    SET    = '/set'

class Session:
    def __init__(self, connection):
        self.sd   = connection[0]
        self.addr = connection[1]
        self.id = self.sd.fileno()
        self.name = ''
        self.room = -1
        self.state = SessionState.START
        self.buf = ''
        self.send_msg('Enter your name: ', True)

    def __del__(self):
        self.sd.close()

    def get_sd(self):
        return self.sd

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_room(self):
        return self.room

    def send_msg(self, msg, prefix=False):
        if prefix:
            msg = '> ' + msg
        self.sd.sendall(msg.replace('\n', '\r\n').encode())

    def handle(self, r, self_r):
        try:
            buf = self.sd.recv(INBUFSIZE)
        except:
            self.state = SessionState.FINISH
            return False

        if not buf:
            self.state = SessionState.FINISH
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

        if self.state == SessionState.LOGIN:
            self.__login(buf)
            self.state = SessionState.CMD
        elif self.state == SessionState.CMD:
            self.__cmd(buf, r)
        elif self.state == SessionState.ROOM:
            self.__chat(buf, self_r)
        else:
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
            self.send_msg('Wrong password\n', True)
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
        if cmd == SessionCmd.QUIT:
            self.send_msg(f'Goodbye {self.name}!\n', True)
            self.state = SessionState.FINISH
        elif cmd == SessionCmd.HELP:
            self.send_msg('Available commands:\n'
                          f'\t\'{SessionCmd.QUIT}\' to quit the server\n'
                          f'\t\'{SessionCmd.HELP}\' to get this help\n'
                          f'\t\'{SessionCmd.NEW}\'  to make default room\n'
                          f'\t\'{SessionCmd.NEW}\'  [$name in \'quotes\'] '
                           '[$pass or nopass] [$max_count]\n'
                          f'\t\'{SessionCmd.LIST}\' to list all rooms\n'
                          f'\t\'{SessionCmd.JOIN}\' [$room_id] to join '
                           'the room without a password\n'
                          f'\t\'{SessionCmd.JOIN}\' [$room_id] '
                           '[optional $pass]\n'
                           '\n\tYou have to write room name in '
                           'quotes: (\' and \").\n'
                           '\tYou can also add backslash to add quote\n'
                           '\tin your room name like "\\"room\\"".\n',
                          True)
        elif cmd == SessionCmd.NEW:
            name, args = partition_quotes(args)
            password, sep, max_count = args.partition(' ')
            try:
                self.__new_room(r, name, password, int(max_count))
            except:
                self.__new_room(r)
        elif cmd == SessionCmd.LIST:
            self.__list_room(r)
        elif cmd == SessionCmd.JOIN:
            try:
                rid, sep, password = args.partition(' ')
                t = room.get_room_by_id(r, int(rid))
                if t:
                    if password:
                        self.__join_room(t, password)
                    else:
                        self.__join_room(t)
                else:
                    self.send_msg('Wrong room id\n', True)
            except:
                self.send_msg(f'Join usage: {SessionCmd.JOIN} [$room_id] '
                               '[optional $pass]\n', True)
        else:
            self.send_msg(f'Invalid command, try \'{SessionCmd.HELP}\'\n',
                          True)

    def __chat(self, buf, r):
        cmd, sep, args = buf.partition(' ')
        if cmd == ChatCmd.QUIT:
            r.kick(self)
        elif cmd == ChatCmd.HELP:
            self.send_msg('Available commands:\n'
                          f'\t\'{ChatCmd.QUIT}\'   to quit the room\n'
                          f'\t\'{ChatCmd.HELP}\'   to get this help\n'
                          f'\t\'{ChatCmd.ONLINE}\' to get users online\n'
                          f'\t\'{ChatCmd.KICK}\'   [$name] [optional $msg] '
                           'to kick user\n'
                          f'\t\'{ChatCmd.OWNER}\'  [$name] to tranship '
                           'the owner\n'
                          f'\t\'{ChatCmd.SET}\'    '
                           '[$name or $pass or $max_count] [$value]\n',
                          True)
        elif cmd == ChatCmd.ONLINE:
            self.send_msg(r.get_online(), True)
        elif cmd == ChatCmd.KICK:
            if not args:
                self.send_msg(f'Kick usage: {ChatCmd.KICK} [$id] '
                               '[optional $msg in \'quotes\']\n',
                              True)
                return

            sess_id, sep, msg = args.partition(' ')
            try:
                sess_id = int(sess_id)
            except:
                self.send_msg(f'Kick usage: {ChatCmd.KICK} [$id] '
                               '[optional $msg in \'quotes\']\n',
                              True)
                return

            if not r.owner_kick(self.name, sess_id, msg):
                self.send_msg(f'You can\'t kick\n', True)
        elif cmd == ChatCmd.OWNER:
            if not args:
                self.send_msg(f'Owner usage: {ChatCmd.OWNER} [name]\n', True)
                return
            if not r.tranship_owner(self.name, args):
                self.send_msg('You can\'t tranship the owner\n', True)
        elif cmd == ChatCmd.SET:
            var, sep, val = args.partition(' ')
            if val:
                if not r.set_var(self, var, val):
                    self.send_msg('You can\'t set variable for this '
                                  'room\n', True)
            else:
                self.send_msg(f'Set usage: {ChatCmd.SET} [$variable] '
                               '[$value]\n', True)
        else:
            if buf and buf[0] != '/':
                r.send_msg(f'\n>> {self.name}: {buf}\n', self)
            else:
                self.send_msg(f'Invalid command, try \'{ChatCmd.HELP}\'\n',
                              True)
