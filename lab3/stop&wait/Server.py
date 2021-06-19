import time
import select
import socket
from random import random
from Data import Data
from Data import split


class Server:
    def __init__(self):
        self.nextseqnum = 1
        self.addr = ('127.0.0.1', 31500)
        self.client_addr = ('127.0.0.1', 12345)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.max_time = 5  # 超时时间
        self.wait_time = 8
        self.pkg_num = 0
        self.buff_size = 1024
        self.theData = None

    def send(self, buffer):
        pkg_timer = 0
        self.pkg_num = len(buffer)
        ackcount = 0
        self.socket.sendto(str(len(buffer)).encode(), self.client_addr)

        while True:
            # 首先判断是否存在超时，如果存在超时，将超时的报文状态置为0，以供之后重发
            if pkg_timer > self.max_time:
                if self.theData is not None and self.theData.state == 1:
                    self.theData.state = 0
                    print('Server: 发生超时，重传', self.theData.seq)
            # 判断是否结束发送
            if self.nextseqnum > self.pkg_num and self.theData.state == 2:
                if pkg_timer > self.wait_time or ackcount == self.pkg_num:
                    print('Server: 发送完毕')
                    break
                continue
            # 判断当前报文是否已经完成接收，准备下一个要发送的数据，包装成Data
            if self.theData is None or self.theData.state == 2:
                self.theData = Data(buffer[self.nextseqnum - 1], 0, seq=self.nextseqnum)
                self.nextseqnum += 1
            # 将状态位为0的报文进行发送
            if not self.theData.state:
                print('Server: 发送数据', self.theData.seq)
                self.socket.sendto(str(self.theData).encode(), self.client_addr)
                self.theData.state = 1
                pkg_timer = 0

            # 以下进行ACK报文的处理
            readable, writeable, errors = select.select([self.socket, ], [], [], 1)
            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                msg = message.decode()
                msgnum, msgtype, msg = split(msg)
                # type = 1 则是 ACk报文
                if msgtype == '1':
                    print('Server: 收到ACK', msgnum)
                    # 记录最新收到的ACK号
                    ack_num = msgnum
                    # 模拟ACK丢包
                    if random() < 0.1:
                        print('Server: 模拟ACK丢失，丢失的ACK为', ack_num)
                        pkg_timer += 1
                        continue
                    if ack_num == self.theData.seq:
                        pkg_timer = 0
                        self.theData.state = 2
                        ackcount += 1
            else:
                pkg_timer += 1

    def start(self):
        buffer = []
        with open('send.txt', 'rb') as f:
            while True:
                seq = f.read(500)
                if len(seq) > 0:
                    buffer.append(seq)
                else:
                    break
        while True:
            # 无阻塞socket连接监控
            readable, writeable, errors = select.select([self.socket, ], [], [], 1)
            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                if message.decode() == '-testsw':
                    self.send(buffer)
                    print('break')
                elif message.decode() == '-quit':
                    self.socket.close()
                    break
                elif message.decode() == '-time':
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    self.socket.sendto(msg.encode(), address)


s = Server()
s.start()
