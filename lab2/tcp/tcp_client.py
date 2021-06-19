import os
import signal
import sys
from socket import *


class tcpClient:
    server_address = ('127.0.0.1', 9090)

    def __init__(self, name):
        self.socket = socket()  # 创建套接字
        self.user_name = name

    def msg_recv(self):
        while True:
            data = self.socket.recv(1024)
            if data.decode('gb2312') == 'exit':
                print('客户端退出')
                break
            print(data.decode('gb2312'))

    def msg_send(self):  # 发送消息
        while True:
            data_info = input()
            self.socket.send(data_info.encode('gb2312'))
            if data_info == 'exit':
                break

    def start(self):
        # 连接至服务器
        try:
            self.socket.connect(self.server_address)
        except Exception:
            print("连接失败 请重试！")
            self.socket.close()
            return
        # 判断是否成功进入聊天室
        while True:
            name = input("请输入用户名:")
            self.socket.send((name + ' -n').encode('gb2312'))
            data = self.socket.recv(128)
            print(data.decode('gb2312'), type(data.decode('gb2312')))
            if data.decode('gb2312') == 'OK':
                print("你已经成功进入聊天室")
                break
            else:
                print(data.decode('gb2312'))

        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        pid = os.fork()

        if pid < 0:
            sys.exit("err")
        elif pid == 0:  # 子进程
            self.msg_recv()
        else:
            print('主进程pid为', pid)
            self.msg_send()


if __name__ == '__main__':
    server1 = tcpClient('sam')
    server1.start()
