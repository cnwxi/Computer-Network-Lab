import time
import select
import socket
from random import random
from Data import Data, split


class SRServer:
    def __init__(self):
        self.nextseqnum = 1
        self.addr = ('127.0.0.1', 31500)
        self.client_addr = ('127.0.0.1', 12345)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.max_time = 5
        self.wait_time = 15
        self.pkg_num = 0
        self.N = 3
        self.M = 3
        self.buff_size = 1024
        self.send_windows = []
        self.receive_windows = []

    def send(self, buffer):
        pkg_timer = []
        self.pkg_num = len(buffer)
        last_ack = 0
        msg_timer = 0
        recData = []
        while True:
            for index, item in enumerate(pkg_timer):
                if item > self.max_time:
                    if self.send_windows[index].state != 2:
                        self.send_windows[index].state = 0
                        print('Server: 发生超时，重传', self.send_windows[index].seq)

            while len(self.send_windows) < self.N:
                if self.nextseqnum > self.pkg_num:
                    break
                data = Data(buffer[self.nextseqnum - 1], 0, seq=self.nextseqnum)
                self.send_windows.append(data)
                pkg_timer.append(0)
                self.nextseqnum += 1

            if not self.send_windows:
                if not pkg_timer and msg_timer > self.wait_time:
                    with open('srSreceive.txt', 'wb') as f:
                        for d in recData:
                            f.write(d.encode())
                    print('Server: 发送/接收完毕, 退出')
                    break

            for index, data in enumerate(self.send_windows):
                if not data.state:
                    print('Server: 发送MSG', data.seq)
                    self.socket.sendto(str(data).encode(), self.client_addr)
                    data.state = 1
                    pkg_timer[index] = 0

            readable, writeable, errors = select.select([self.socket, ], [], [], 1)

            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                msg = message.decode()
                msgnum, msgtype, msg = split(msg)
                if msgtype == '1':
                    ack_num = msgnum
                    print('Server: 收到ACK', msgnum)
                    if len(self.send_windows) == 0:
                        continue
                    if random() < 0.1:
                        print('Client: 模拟ACK丢失，丢失ACK为', str(ack_num))
                        for index, item in enumerate(pkg_timer):
                            if self.send_windows[index].state != 2:
                                pkg_timer[index] = item + 1
                        continue
                    if int(ack_num) < int(self.send_windows[0].seq):
                        continue
                    pkg_timer[int(ack_num) - int(self.send_windows[0].seq)] = 0
                    for i in range(len(self.send_windows)):
                        if ack_num == self.send_windows[i].seq:
                            self.send_windows[i].state = 2
                            if i == 0:
                                idx = 0
                                flag = 1
                                for idx in range(len(self.send_windows)):
                                    if self.send_windows[idx].state != 2:
                                        flag = 0
                                        break
                                idx += flag
                                self.send_windows = self.send_windows[idx:]
                                pkg_timer = pkg_timer[idx:]
                            break
                else:
                    for index, item in enumerate(pkg_timer):
                        if self.send_windows[index].state != 2:
                            item += 1
                    print('Server: 收到MSG', msgnum)
                    seqNum = int(msgnum)
                    if random() < 0.1:
                        print('Client: 模拟发生丢包, 丢失的包的seq为', str(seqNum))
                        msg_timer += 1
                        continue
                    msg_timer = 0
                    if last_ack == seqNum - 1:
                        toRemove = []
                        recData.insert(seqNum - 1, msg)
                        self.socket.sendto(str(Data(''.encode(), 1, seqNum)).encode(), address)  # 返回ACK
                        print('Server: 发送ACK', str(seqNum))
                        self.receive_windows.append(seqNum)
                        for i in range(self.M):
                            if (seqNum + i) not in self.receive_windows:
                                last_ack = seqNum + i - 1
                                break
                            else:
                                last_ack = seqNum + i
                                toRemove.append((seqNum + i))
                        for ele in toRemove:
                            self.receive_windows.remove(ele)
                    else:
                        if (last_ack + 1 + self.M) > seqNum > last_ack and seqNum not in self.receive_windows:
                            self.receive_windows.append(seqNum)
                            recData.insert(seqNum - 1, msg)
                            print('Server: 缓存数据', seqNum)

                            self.socket.sendto(str(Data(''.encode(), 1, seqNum)).encode(), address)
                        elif seqNum <= last_ack:
                            self.socket.sendto(str(Data(''.encode(), 1, seqNum)).encode(), address)
                        else:
                            print('Server 扔弃', seqNum)
            else:
                for index, item in enumerate(pkg_timer):
                    if self.send_windows[index].state != 2:
                        pkg_timer[index] = item + 1
                msg_timer += 1

    def start(self):
        buffer = []
        with open('server_send.txt', 'rb') as f:
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
                if message.decode() == '-testsr':
                    self.send(buffer)
                    print('break')
                    time.sleep(2)
                elif message.decode() == '-quit':
                    self.socket.close()
                    break
                elif message.decode() == '-time':
                    msg = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    self.socket.sendto(msg.encode(), address)


s = SRServer()
s.start()
