from time import sleep
import select
import socket
from random import random
from Data import Data, split


class Client:
    def __init__(self):
        self.nextseqnum = 1
        self.addr = ('127.0.0.1', 12345)
        self.server_addr = ('127.0.0.1', 31500)
        self.max_time = 5  # 超时时间
        self.wait_time = 8  # 等待看是否还有数据发来的时间
        self.pkg_num = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)
        self.buff_size = 1024
        self.revData = ''

    def receive(self):
        last_ack = 0
        msg_timer = 0
        recvcount = 0
        while True:
            readable, writeable, errors = select.select([self.socket, ], [], [], 1)
            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                msg = message.decode()
                recvamount = int(msg)
                break

        while True:
            if recvcount == recvamount and msg_timer > self.wait_time:
                with open('receive.txt', 'wb') as f:
                    f.write(self.revData.encode())
                print('Client: 接收完毕')
                break
            readable, writeable, errors = select.select([self.socket, ], [], [], 1)
            if len(readable) > 0:
                message, address = self.socket.recvfrom(self.buff_size)
                msg = message.decode()
                msgnum, msgtype, msg = split(msg)
                if msgtype == '0':
                    print('Client: 收到MSG=', msgnum, '/', recvamount)
                    ack_num = int(msgnum)
                    if last_ack == ack_num - 1:
                        if random() < 0.1:
                            print('Client: 模拟发生丢包, 丢失的包的seq为', str(ack_num))
                            continue
                        msg_timer = 0
                        self.socket.sendto(str(Data(''.encode(), 1, ack_num)).encode(), address)
                        print('Client: 发送ACK ', str(ack_num))
                        recvcount += 1
                        last_ack = ack_num
                        self.revData += msg
                    else:
                        msg_timer = 0
                        print('Client: 收到的MSG不是需要的，发送当前收到的最大的ACK', last_ack)
                        self.socket.sendto(str(Data(''.encode(), 1, last_ack)).encode(), address)
            else:
                msg_timer += 1

    def start(self):
        self.socket.sendto('-time'.encode(), self.server_addr)
        print('send -time')
        msg = self.socket.recv(self.buff_size).decode()
        print(msg)
        self.socket.sendto('-testsw'.encode(), self.server_addr)
        print('send -testsw')
        self.receive()
        sleep(5)
        self.socket.sendto('-quit'.encode(), self.server_addr)
        print('send -quit')
        self.socket.close()


c = Client()
c.start()
