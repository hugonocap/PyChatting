import session

class Room:
    def __init__(self, rid, sess_name):
        self.id = rid
        self.name = f'{sess_name}\'s room'
        self.sess = []

    def __del__(self):
        while self.sess:
            self.kick(self.sess[0])

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def count(self):
        return len(self.sess)

    def add_session(self, sess):
        self.sess.append(sess)

    def remove_session(self, sess):
        self.sess.remove(sess)

    def kick(self, sess):
        sess.leave_room()
        self.remove_session(sess)

    def refresh(self):
        i = 0
        while i < len(self.sess):
            if self.sess[i].get_room() != self.id:
                self.remove_session(self.sess[i])
            else:
                i += 1

    def send_msg(self, msg, exception):
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
