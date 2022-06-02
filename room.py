import session

class Room:
    def __init__(self, rid, sess):
        self.id = rid
        self.name = f'{sess.name}\'s room'
        self.sess = [sess]

    def __del__(self):
        while self.sess:
            self.kick(self.sess[0])

    def get_id(self):
        return self.id

    def count(self):
        return len(self.sess)

    def remove_sess(self, sess):
        self.sess.remove(sess)

    def kick(self, sess):
        sess.leave_room()
        self.remove_sess(sess)

    def refresh(self):
        i = 0
        while i < len(self.sess):
            if self.sess[i].get_room() != self.id:
                self.remove_sess(self.sess[i])
            else:
                i += 1
