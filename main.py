import sys, select, socket

INBUFSIZE = 1024
LISTENQUEUE = 32

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

class Server:
    def __init__(self):
        try:
            self.ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ls.bind((sys.argv[1], int(sys.argv[2])))
            self.ls.listen(LISTENQUEUE)
        except:
            print(socket.error, file=sys.stderr)
            quit(1)
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
                break;

            if self.ls in slist[0]:
                self.accept_client()
                rlist.append(self.sess[len(self.sess)-1].sd)

            for sess in self.sess:
                if sess.sd in slist[0]:
                    if not sess.handle():
                        self.close_session(sess)
                        rlist.remove(sess.sd)

    def accept_client(self):
        self.sess.append(Session(self.ls.accept()))

    def close_session(self, sess):
        self.sess.remove(sess)
        del sess

if len(sys.argv) < 3:
    print('Error. Usage: serv [ip] [port]', file=sys.stderr)
    quit(1)

serv = Server()
serv.run()
del serv

quit()
