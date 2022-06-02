import sys, socket, select

import session

LISTENQUEUE = 32

class Server:
    def __init__(self, ip, port):
        try:
            self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ls.bind((ip, port))
            self.ls.listen(LISTENQUEUE)
        except socket.error as err:
            print(err, file=sys.stderr)
            return
        self.sess = []

    def __del__(self):
        self.ls.close()
        for s in self.sess:
            self.close_session(s)

    def run(self):
        rlist = [self.ls]

        while True:
            try:
                slist = select.select(rlist, [], [])
            except KeyboardInterrupt:
                break

            if self.ls in slist[0]:
                self.accept_client()
                rlist.append(self.sess[len(self.sess)-1].sd)

            for sess in self.sess:
                if sess.sd in slist[0]:
                    if not sess.handle():
                        self.close_session(sess)
                        rlist.remove(sess.sd)

    def accept_client(self):
        self.sess.append(session.Session(self.ls.accept()))

    def close_session(self, sess):
        self.sess.remove(sess)
        del sess
