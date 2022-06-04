from common import *
import session

class RoomVariable:
    NAME      = '$name'
    PASS      = '$pass'
    MAX_COUNT = '$max_count'

class Room:
    def __init__(self, rid, owner, name, password, max_count):
        self.id = rid
        self.owner = owner
        self.name = name
        self.password = password
        self.max_count = max_count
        self.sess = []

    def __del__(self):
        while self.sess:
            self.kick(self.sess[0])

    def __is_owner(self, sess):
        return self.owner == sess.get_id()

    def __get_sess_by_id(self, sid):
        for sess in self.sess:
            if sess.get_id() == sid:
                return sess
        return None

    def __set_owner(self, sid):
        self.owner = sid

    def __check_owner(self):
        if not self.__get_sess_by_id(self.owner) and self.sess:
            self.__set_owner(self.sess[0].get_id())
            self.sess[0].send_msg('You are room owner now\n', True)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def has_password(self):
        return self.password != 'nopass'

    def check_password(self, password):
        return not self.has_password() or self.password == password

    def get_max_count(self):
        return self.max_count

    def count(self):
        return len(self.sess)

    def get_info(self):
        buf = f'[{self.id}] {self.name} ({self.count()}/{self.max_count}) '
        if self.has_password():
            buf += 'PASSWORD'
        else:
            buf += 'NO PASSWORD'
        return buf

    def get_online(self):
        buf = f'{self.get_info()}:\n'
        for sess in self.sess:
            buf += f'\t[{sess.id}] {sess.name}'
            if self.__is_owner(sess):
                buf += ' *OWNER'
            buf += '\n'
        return buf

    def set_var(self, sid, var, val):
        if not self.__is_owner(sid):
            return False
        if var == RoomVariable.NAME:
            val, tmp = partition_quotes(val)
            self.name = val
        elif var == RoomVariable.PASS:
            self.password = val
        elif var == RoomVariable.MAX_COUNT:
            self.max_count = val
        return True

    def add_session(self, sess):
        if self.count() < self.max_count:
            self.sess.append(sess)
            self.send_msg(f'{sess.get_name()} has joined our room!\n',
                          sess, True)
            return True
        return False

    def remove_session(self, sess):
        self.sess.remove(sess)
        self.send_msg(f'{sess.get_name()} has left the room...\n', sess, True)

    def kick(self, sess):
        sess.leave_room()
        self.remove_session(sess)

    def owner_kick(self, who, whom, msg=''):
        msg, tmp = partition_quotes(msg)
        sess = self.__get_sess_by_id(whom)
        if who == self.owner and sess:
            self.kick(sess)
            if msg:
                sess.send_msg(f'You were kicked with msg: {msg}\n', True)
            return True
        return False

    def tranship_owner(self, who, whom):
        sess = self.__get_sess_by_id(whom)
        if who == self.owner and sess:
            self.__set_owner(whom)
            sess.send_msg(f'{who} transhiped you room owner\n', True)
            return True
        return False

    def refresh(self):
        i = 0
        while i < len(self.sess):
            if self.sess[i].get_room() != self.id:
                self.remove_session(self.sess[i])
            else:
                i += 1
        self.__check_owner()

    def send_msg(self, msg, exception, prefix=False):
        if prefix:
            msg = '\n> ' + msg
        for sess in self.sess:
            if sess != exception:
                sess.send_msg(msg)

def get_free_rid(r):
    last = -1
    for t in r:
        if t.get_id() - last > 1:
            break
        last = t.get_id()
    return last+1

def get_room_by_id(r, rid):
    for t in r:
        if t.get_id() == rid:
            return t
    return None
