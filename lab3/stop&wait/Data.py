class Data(object):
    def __init__(self, msg, type, seq=0, state=0):
        self.msg = msg.decode()  # 报文内容
        self.type = str(type)  # 报文类型 数据MSG/相应ACK
        self.seq = str(seq)  # 序列号或者ACK号
        self.state = state  # 报文状态 0 未发送、1 已发送未收到ACK、2 已发送并收到ACK

    def __str__(self):
        return self.seq + '|' + self.type + '|' + self.msg


def split(msg):
    pieces = msg.split('|')
    seq, type, msg = pieces
    return seq, type, msg
