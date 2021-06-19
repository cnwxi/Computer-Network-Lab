import socket
import time


def main():
    # 创建套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', 7891))
    address = ('127.0.0.1', 7890)
    # 10.63.101.36
    server_socket.sendto("100".encode('utf-8'), address)
    for i in range(1, 101):
        send_data = None
        send_data = str(i) + " of the packet sent from server"
        # if i == 99:
        #     time.sleep(5)

        print(send_data)
        server_socket.sendto(send_data.encode('utf-8'), address)
    server_socket.close()


if __name__ == '__main__':
    main()
