class Data(object):
    def __init__(self, msg, type, seq=0, state=0):
        self.msg = msg.decode()
        self.type = str(type)
        self.seq = str(seq)
        self.state = state

    def __str__(self):
        return self.seq + '|' + self.type + '|' + self.msg


def split(msg):
    pieces = msg.split('|')
    seq, type, msg = pieces
    return seq, type, msg
