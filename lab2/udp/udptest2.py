import socket
import sys
import threading
import tkinter as tk
from tkinter import END


def main():
    root = tk.Tk()
    root.title('udp聊天:test2')

    message_frame = tk.Frame(width=480, height=300, bg='white')
    text_frame = tk.Frame(width=480, height=100)
    send_frame = tk.Frame(width=480, height=30)
    quit_frame = tk.Frame(width=480, height=30)
    global text_message
    text_message = tk.Text(message_frame)
    global text_text
    text_text = tk.Text(text_frame)
    button_send = tk.Button(send_frame, text='发送', command=send)
    button_quit = tk.Button(quit_frame, text='退出', command=quit)
    message_frame.grid(row=0, column=0, padx=3, pady=6)
    text_frame.grid(row=1, column=0, padx=3, pady=6)
    send_frame.grid(row=2, column=0)
    quit_frame.grid(row=3, column=0)

    message_frame.grid_propagate(0)
    text_frame.grid_propagate(0)
    send_frame.grid_propagate(0)
    quit_frame.grid_propagate(0)

    text_message.grid()
    text_text.grid()
    button_send.grid()
    button_quit.grid()
    # 创建套接字
    global udp_socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定信息
    udp_socket.bind(("", 7890))

    t = threading.Thread(target=recv_msg, args=(udp_socket,))
    t.start()

    root.mainloop()


def send():
    global text_text, udp_socket, text_message
    send_data = 'test2:' + text_text.get('1.0', END)
    address = ('127.0.0.1', 7891)
    # 获取要发送的内容+
    udp_socket.sendto(send_data.encode("utf-8"), address)
    text_message.insert(END, send_data)
    text_text.delete('1.0', END)


def quit():
    global udp_socket
    address = ('127.0.0.1', 7891)
    udp_socket.sendto("对方已下线".encode("utf-8"), address)
    udp_socket.close()
    sys.exit()


def recv_msg(udp_socket):
    """接收数据"""
    global text_message
    while True:
        recv_data, address = udp_socket.recvfrom(1024)
        text_message.insert(END, recv_data.decode('utf-8'))


if __name__ == '__main__':
    main()
