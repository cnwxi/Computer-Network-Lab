from socket import *
from threading import Thread
from os import *
import sys

online = True


class Client:

    def __init__(self, ip="127.0.0.1", port=8888):
        self.code = "utf-8"
        self.address = (ip, port)
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def recv(self):
        global online
        while online:
            data = self.client_socket.recv(1024).decode(self.code)
            if data != "quit":
                print("<<" + data)
            else:
                break
        self.client_socket.close()

    def send(self):
        global online
        while True:
            data = input(">>")
            self.client_socket.send(data.encode(self.code))
            if data == "quit":
                break
        online = False
        self.client_socket.close()
        sys.exit()

    def start(self):
        self.client_socket.connect(self.address)
        threadRecv = Thread(target=self.recv)
        threadSend = Thread(target=self.send)
        threadRecv.start()
        threadSend.start()
        # 连接服务器


# ip = input("ip:")
# port = int(input("port:"))
# my_socket = Client(ip, port)
client = Client()
client.start()
