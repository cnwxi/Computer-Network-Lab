from time import sleep

import select
import socket
import sys
from random import random
from Data import Data
from Data import split


class GBNClient:
    def __init__(self):
        self.nextseqnum = 1
        self.addr = ('127.0.0.1', 12345)
        self.server_addr = ('127.0.0.1', 31500)
        self.max_time = 5  # 超时时间
        self.wait_time = 8  # 等待看是否还有数据发来的时间
        self.pkg_num = 0
        self.N = 3
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.buff_size = 1024
        self.send_windows = []
        self.revData = ''

    def send(self, buffer):

        # 计时和包序号初始化
        pkg_timer = 0
        self.pkg_num = len(buffer)
        # 记录上一个回执的ack的值
        last_ack = 0
        msg_timer = 0

        while True:
            # 当超时后，将窗口内的数据更改为未发送状态
            if pkg_timer > self.max_time:
                resend = []
                for data in self.send_windows:
                    data.state = 0
                    resend.append(data.seq)
                if len(resend) > 0:
                    print('Client: 发生超时，重传', resend)

            # 窗口中数据少于最大容量时，尝试添加新数据
            while len(self.send_windows) < self.N:
                if self.nextseqnum > self.pkg_num:
                    break
                # 将第nextseqnum-1个包加入窗口内，并封装成数据,type为0
                data = Data(buffer[self.nextseqnum - 1], 0, seq=self.nextseqnum)
                self.send_windows.append(data)
                self.nextseqnum += 1

            # 窗口内无数据则退出总循环
            if not self.send_windows:
                if pkg_timer > self.max_time and msg_timer > self.wait_time:
                    with open('gbnCreceive.txt', 'wb') as f:
                        f.write(self.revData.encode())
                    print('Client: 发送/接收完毕, 退出')
                    break

            # 遍历窗口内数据，如果存在未成功发送的则发送
            for data in self.send_windows:
                if not data.state:
                    print('Client: 发送MSG', data.seq)
                    self.socket.sendto(str(data).encode(), self.server_addr)
                    data.state = 1

            # 无阻塞socket连接监控
            readable, writeable, errors = select.select([self.socket, ], [], [], 1)

            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                msg = message.decode()
                msgnum, msgtype, msg = split(msg)
                if msgtype == '1':
                    # 收到ACK， 重新计时
                    print('Client: 收到ACK', msgnum)
                    ack_num = msgnum
                    if random() < 0.1:  # ack丢失
                        print('Client: 模拟ACK丢失，丢失ACK为', str(ack_num))
                        pkg_timer += 1
                        continue
                    pkg_timer = 0
                    for i in range(len(self.send_windows)):
                        if ack_num == self.send_windows[i].seq:
                            self.send_windows = self.send_windows[i + 1:]
                            break
                else:
                    # 非ACK，说明是收到的数据
                    pkg_timer += 1
                    print('Client: 收到MSG', msgnum)
                    seqNum = int(msgnum)
                    if random() < 0.1:
                        print('Client: 模拟发生丢包, 丢失的包的seq为', str(seqNum))
                        continue
                    if last_ack == seqNum - 1:
                        msg_timer = 0
                        self.socket.sendto(str(Data(''.encode(), 1, seqNum)).encode(), address)
                        print('Client: 发送ACK', str(seqNum))
                        last_ack = seqNum
                        self.revData += msg
                    else:
                        print('Client: 收到的MSG不是需要的，发送当前收到的最大的ACK ', last_ack)
                        self.socket.sendto(str(Data(''.encode(), 1, last_ack)).encode(), address)
            else:
                # 未收到数据则计时器加一
                pkg_timer += 1
                msg_timer += 1

    def start(self):
        # 读取文件
        buffer = []
        with open('client_send.txt', 'rb') as f:
            while True:
                seq = f.read(500)
                if len(seq) > 0:
                    buffer.append(seq)
                else:
                    break
        self.socket.sendto('-time'.encode(), self.server_addr)
        print('send -time')
        msg = self.socket.recv(self.buff_size).decode()
        print(msg)
        self.socket.sendto('-testgbn'.encode(), self.server_addr)
        print('send -testbgn')
        self.send(buffer)
        sleep(8)
        self.socket.sendto('-quit'.encode(), self.server_addr)
        print('send -quit')
        sleep(3)
        self.socket.close()


c = GBNClient()
c.start()
