from sys import stderr
import socket
from select import select

import session, room

LISTENQUEUE = 32

class Server:
    def __init__(self, address):
        self.sess = []
        self.room = []
        try:
            self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ls.bind(address)
            self.ls.listen(LISTENQUEUE)
        except socket.error as err:
            self.ls.close()
            print(err, file=stderr)
            return

    def __del__(self):
        self.ls.close()
        while self.sess:
            self.__close_session(0)

    def init_success(self):
        return self.ls.fileno() > -1

    def run(self):
        rlist = [self.ls]

        while True:
            try:
                slist = select(rlist, [], [])
            except KeyboardInterrupt:
                break

            if self.ls in slist[0]:
                if self.__accept_client():
                    rlist.append(self.sess[len(self.sess)-1].sd)

            i = 0
            while i < len(self.sess):
                if self.sess[i].get_sd() in slist[0]:
                    r = self.__get_room_by_session(self.sess[i])
                    if not self.sess[i].handle(self.room, r):
                        rlist.remove(self.sess[i].get_sd())
                        self.__close_session(i)
                        i -= 1
                i += 1

            self.__handle_room()

    def __accept_client(self):
        try:
            self.sess.append(session.Session(self.ls.accept()))
            return True
        except:
            return False

    def __get_room_by_session(self, sess):
        rid = sess.get_room()
        for r in self.room:
            if r.get_id() == rid:
                return r
        return None

    def __close_session(self, i):
        if r := self.__get_room_by_session(self.sess[i]):
            r.kick(self.sess[i])
        self.sess.pop(i)

    def __handle_room(self):
        i = 0
        while i < len(self.room):
            r = self.room[i]
            r.refresh()
            if r.count() <= 0:
                self.room.remove(r)
            else:
                i += 1
