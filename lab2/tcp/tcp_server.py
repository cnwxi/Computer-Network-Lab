import sys
import time
from socket import *
from threading import Thread


class Node:
    def init(self):
        self.Name = None
        self.Ip = None
        self.Thr = None


class tcpServer():
    user_name = {}  # dict 用户名:对象
    jobs = {}  # 存储线程对象

    def __init__(self, post):
        self.ServerPort = post
        self.tcp_socket = socket()  # tcp套接字
        self.tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 端口重用
        self.tcp_socket.bind(self.ServerPort)

    def start(self):
        self.tcp_socket.listen(5)
        print(self.getTime(), '系统：等待连接')
        while True:
            try:
                conn, addr = self.tcp_socket.accept()
            except KeyboardInterrupt:
                self.tcp_socket.close()
                sys.exit('\n' + self.getTime() + '系统：服务器安全退出')
            except Exception as e:
                print(e)
                continue

            t = Thread(target=self.do_request, args=(conn,))
            t.start()

            self.jobs[conn] = t
            for c in self.jobs:
                if c._closed is True:
                    self.jobs[c].join()

    def do_request(self, conn):
        connNode = Node()
        while True:
            recv_data = conn.recv(1024).decode('gb2312').strip()
            dest_ip = conn.getpeername()
            info_list = recv_data.split(' ')  # 切割命令

            if recv_data == 'exit':
                print(self.getTime() + ' 系统：用户' + connNode.Name + '退出')
                conn.send('exit'.encode('gb2312'))
                self.user_name.pop(connNode.Name)
                conn.close()
                break
            else:
                try:
                    A = info_list[-2], info_list[-1]
                except IndexError:
                    conn.send((self.getTime() + ' 系统：无法识别您的指令，请重新输入！').encode('gb2312'))
                    continue

            if info_list[-2] == '-t':
                if info_list[-1] not in self.user_name.keys():  # 目前查询不到目标用户，向发送用户发起警告
                    data_info = self.getTime() + ' 系统：发送失败！用户不存在！'
                    conn.send(data_info.encode('gb2312'))
                    continue
                destNode = self.user_name[info_list[-1]]  # 接收方端口
                data_info = self.getTime() + ' %s：' % connNode.Name + ' '.join(info_list[:-2])  # 需发送的信息
                print(self.getTime() + ' 系统：%s发送信息给了%s' % (connNode.Name, info_list[-1]))
                destNode.Thr.send(data_info.encode('gb2312'))
            elif info_list[-1] == '-n':
                # 新用户注册
                print(self.getTime() + ' 系统：' + info_list[0] + '连接成功')
                data_info = self.getTime() + ' 系统：' + info_list[0] + '加入了聊天'
                self.sent_to_all(data_info)
                conn.send('OK'.encode('gb2312'))
                connNode.Name = info_list[0]
                connNode.Ip = dest_ip
                connNode.Thr = conn
                self.user_name[info_list[0]] = connNode
            elif info_list[-1] == '-ta':
                # 群发消息
                data_info = self.getTime() + ' %s：' % connNode.Name + ' '.join(info_list[:-1])
                self.sent_to_all_notMe(connNode.Name, data_info)

    def getTime(self):
        return '[' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']'

    def sent_to_all(self, data_info):
        # 系统广播信息
        print(self.getTime() + ' 系统：群发信息给了', end='')
        for i in self.user_name.values():
            print(i.Name + '、', end='')
            i.Thr.send(data_info.encode('gb2312'))
        print()

    def sent_to_all_notMe(self, name, data_info):
        # 广播消息除了指定用户
        print(self.getTime() + ' 系统：群发信息给了', end='')
        for i in self.user_name.values():
            if i.Name != name:
                print(i.Name + '、', end='')
                i.Thr.send(data_info.encode('gb2312'))
        print()


if __name__ == '__main__':
    Host = '127.0.0.1'
    Post = 9090
    server1 = tcpServer((Host, Post))
    server1.start()
