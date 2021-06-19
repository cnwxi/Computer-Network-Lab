import sys
from socket import *
from threading import Thread

end = False


class Client:
    def __init__(self, ip="127.0.0.1", port=8888):
        """
        :param ip: 服务端地址
        :param port: 服务端ip
        """
        self.code = "utf-8"
        self.address = (ip, port)
        """
        创建套接字
        套接字类型有两种类型——基于文件和面向网路的
        面向网络的 AF_INET,AF_INET6(用于IPv6)
        面向连接的套接字——TCP套接字的名字SOCK_STREAM。
        无连接的套接字——UDP套接字的名字SOCK_DGRAM
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def recv(self):
        """
        从服务端接受信息
        使用recv接收数据，参数为缓冲区大小
        是阻塞方式
        """
        global end
        while True:
            data = self.client_socket.recv(1024).decode(self.code)
            if data != "quit":
                print("<<" + data)
            else:
                print("quit")
                end = True
                break

    def send(self):
        """
        往服务器发送信息
        使用send往目的端发送数据，返回值为已发送的字符个数
        """
        while True:
            data = input(">>")
            self.client_socket.send(data.encode(self.code))
            if data == "quit":
                self.client_socket.send(data.encode(self.code))
                break

    def start(self):
        """
        使用connect与服务器创建连接，参数为（目的ip，目的端口）
        :return:
        """
        self.client_socket.connect(self.address)
        threadRecv = Thread(target=self.recv)
        threadRecv.setDaemon(True)
        threadSend = Thread(target=self.send)
        threadSend.setDaemon(True)
        """
        使用两个线程来收发信息。
        """
        threadRecv.start()
        threadSend.start()
        while not end:
            tmp = 1
        self.client_socket.close()


# ip = input("ip:")
# port = int(input("port:"))
# my_socket = Client(ip, port)
client = Client()
client.start()
