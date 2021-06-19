import socket
from datetime import datetime
import threading

timeOut = False
count = 0
num = 0
finished = False
# 标识符,是否完成传输
sender = None


def recv(client_socket):
    global count, num, finished, sender
    while True:
        recv_data, address = client_socket.recvfrom(1024)
        recv_data = recv_data.decode('utf-8')
        if recv_data is not None and address == sender:
            count += 1
            data = str(count) + " packets received"
            print(data)
        print("%s:%s" % (str(address), recv_data))
        if count == num:
            finished = True
            print("接收完毕")
            break
    client_socket.close()


def time(start):
    # 是否超时
    global count, num
    while True:
        now = datetime.now()
        # 从开始接收到目前的时间差大于5s,则认为网络不稳定,出现丢包现象
        if (now - start).seconds >= 5:
            print("time out")
            break
        if finished:
            # 如果标识符为真,则接收线程已经完成所有的接收任务
            print(now - start)
            # 输出一下现在的时间消耗
            break
    # 统计一下接收到的结果
    print(count, "of", num, "received")


def main():
    global count, num, sender
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(('', 7890))
    count = 0

    print('开始接收')
    recv_data, sender = client_socket.recvfrom(1024)
    num = int(recv_data.decode('utf-8'))
    # num = 100
    print("从", sender, "发送的数据包有", num, "个")
    start = datetime.now()
    # for i in range(num):
    #     recv_data, address = client_socket.recvfrom(1024)
    #     now = datetime.now()
    #     if recv_data.decode('utf-8') == "END":
    #         print('结束接收')
    #         break
    #     if (now - start).seconds > 5:
    #         print('超时结束接收')
    #         break
    #     if recv_data is not None:
    #         print("%s:%s" % (str(address), recv_data.decode("utf-8")))
    #         count += 1
    #     else:
    #         print("failed receive")
    t2 = threading.Thread(target=time, args=(start,))
    t1 = threading.Thread(target=recv, args=(client_socket,))
    t1.setDaemon(True)
    t2.start()
    t1.start()
    t2.join()


if __name__ == '__main__':
    main()
