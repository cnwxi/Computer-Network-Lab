from socket import *
from threading import Thread
from time import *

end = False


class Server:
    def __init__(self, port=8888):
        self.c = []
        self.code = 'utf-8'
        self.port = port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        # self.server_socket.setblocking(False)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)
        # 设置端口复用
        """
        端口复用允许在一个应用程序可以把 n 个套接字绑在一个端口上而不出错。同时，这 n 个套接字发送信息都正常，没有问题。但是，这些套接字并不是所有都能读取信息，只有最后一个套接字会正常接收数据。
        端口复用最常用的用途应该是防止服务器重启时之前绑定的端口还未释放或者程序突然退出而系统没有释放端口。
        一般来说，一个端口释放后会等待两分钟之后才能再被使用，SO_REUSEADDR是让端口释放后立即就可以被再次使用。
        """
        self.server_socket.bind(("", self.port))
        # 绑定ip和port
        self.server_socket.listen(5)
        """
        listen函数使用主动连接套接口变为被连接套接口，使得一个进程可以接受其它进程的请求，从而成为一个服务器进程。
        """
        print("等待连接")
        self.threads = []

    def send(self, client_socket, client_address, data):
        data = str(client_address[0]) + ':' + str(client_address[1]) + '|' + data
        for i in self.c:
            if i != (client_socket, client_address):
                i[0].send(data.encode(self.code))

    def end(self):
        global end
        data = "quit"
        for i in self.c:
            i[0].send(data.encode('utf-8'))
        end = True
        self.c.clear()

    def recv(self, client_socket, client_address):
        while True:
            data = client_socket.recv(1024).decode(self.code)
            if data == 'quit':
                break
            else:
                print(client_address, "send:", data)
                self.send(client_socket, client_address, data)

        client_socket.send("quit".encode('utf-8'))
        print("服务于", client_address, "的线程终止")
        print(client_address, "offline")
        self.c.remove((client_socket, client_address))
        sleep(100)
        client_socket.close()

    def cmd(self):
        address = ("host", 8888)
        while True:
            cmd = input(">>")
            if cmd == 'end':
                self.end()
            else:
                self.send(None, address, cmd)

    def server(self):
        global end
        while not end:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(client_address, "online")
                print(client_socket, client_address)
                self.c.append((client_socket, client_address))
                threadRecv = Thread(target=self.recv, args=(client_socket, client_address))
                threadRecv.start()
            except BlockingIOError:
                pass
        self.server_socket.close()

    def start(self):
        global end
        threadCmd = Thread(target=self.cmd)
        threadCmd.setDaemon(True)
        threadSer = Thread(target=self.server)
        threadSer.setDaemon(True)
        threadCmd.start()
        threadSer.start()
        while not end:
            a = 1


# port = int(input("输入port:"))
# server = Server(port)
server = Server()
server.start()
