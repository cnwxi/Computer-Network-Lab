# ！！！默认监听 8080 端口，将浏览器代理设置127.0.0.1:8080即可使用！！！
# 待改进的地方：
#   没有处理CONNECT方法
#   没有实现代理Pipelining
#   没有实现代理连接复用(Keep-Alive)
#   缓存实现的很粗糙，没有验证缓存失效
#   多线程改成协程, 现在的多线程性能太低
# 现在也很不错了，有多线程，有考虑粘包，支持chunked
import threading
from socket import *

headers_end_tag_str = "\r\n\r\n"
headers_end_tag = headers_end_tag_str.encode()
line_end_tag_str = "\r\n"
line_end_tag = line_end_tag_str.encode()


def get_header(packet_headers: str, header: str) -> str:
    return packet_headers.split(header + ": ")[1].split(line_end_tag_str)[0]


def read_socket_for(read_socket: socket, read_for: bytes) -> bytes:
    result = "".encode()
    while True:
        new_read = read_socket.recv(2048)
        result = result + new_read
        if new_read.find(read_for) != -1:
            return result


def make_request(target_host, send_data):
    agent_socket = socket(AF_INET, SOCK_STREAM)
    if ":" in target_host:
        target_host, port = target_host.split(":")
        port = int(port)
    else:
        port = 80
    agent_socket.connect((target_host, port))
    agent_socket.send(send_data)
    packet = read_socket_for(agent_socket, headers_end_tag)
    response_header_end = packet.find(headers_end_tag) + len(headers_end_tag)
    response_header = packet[:response_header_end]
    response_header_str = response_header.decode()
    if "Transfer-Encoding: chunked" in response_header_str:
        current_position = response_header_end
        while True:
            while packet.find(line_end_tag, current_position) == -1:
                packet += read_socket_for(agent_socket, line_end_tag)
            line_end = packet.find(line_end_tag, current_position)
            next_block_length = packet[current_position:line_end].decode()
            next_block_length = int(next_block_length, 16)
            current_position = line_end + len(line_end_tag)
            if next_block_length == 0:
                current_position += len(line_end_tag)
                while len(packet) < current_position:
                    packet += agent_socket.recv(current_position - len(packet))
                break
            else:
                current_position += next_block_length + len(line_end_tag)
                while len(packet) < current_position:
                    packet += agent_socket.recv(current_position - len(packet))

    else:
        content_length = get_header(response_header_str, "Content-Length")
        content_length = int(content_length)
        total_length = len(response_header) + content_length
        while len(packet) < total_length:
            packet += agent_socket.recv(total_length - len(packet))
    agent_socket.close()
    return packet


def proxy_agent(client_socket: socket):
    packet_left: bytes = "".encode()
    try:
        while True:
            # 残包， 用于处理客户端pipelining情况下的粘包
            while packet_left.find(headers_end_tag) == -1:
                packet_left += read_socket_for(client_socket, headers_end_tag)
            first_line_end = packet_left.find(line_end_tag)
            first_line = packet_left[:first_line_end].decode()
            print(first_line)
            (method, path, version) = first_line.split(" ")
            headers_end = packet_left.find(headers_end_tag) + len(headers_end_tag)
            packet_headers = packet_left[:headers_end]
            packet_headers_str = packet_headers.decode()
            packet_left = packet_left[headers_end:]
            if method == "GET":
                cache_lock.acquire()
                if path in cache:
                    response = cache[path]
                    cache_lock.release()
                    print("cache hit")
                    client_socket.send(response)
                else:
                    cache_lock.release()
                    print("cache miss")
                    target_host = get_header(packet_headers_str, "Host")
                    response = make_request(target_host, packet_headers)
                    with cache_lock:
                        cache[path] = response
                    client_socket.send(response)
            elif method == "POST":
                content_length = get_header(packet_headers_str, "Content-Length")
                content_length = int(content_length)
                while len(packet_left) < content_length:
                    packet_left += client_socket.recv(content_length - len(packet_left))
                packet_body = packet_left
                packet_left = packet_left[-1:]
                target_host = get_header(packet_headers_str, "Host")
                response = make_request(target_host, packet_headers + packet_body)
                client_socket.send(response)
            else:
                print("unknown method")
    finally:
        client_socket.close()


def main():
    with socket(AF_INET, SOCK_STREAM) as server_socket:
        server_socket.bind(("", 8080))
        server_socket.listen()
        while True:
            print("Ready to serve...")
            client_socket, addr = server_socket.accept()
            print("Received a connection from: {}".format(addr))
            threading.Thread(target=proxy_agent, args=(client_socket,)).start()


if __name__ == '__main__':
    cache = {}
    cache_lock = threading.Lock()
    print("！！！默认监听 8080 端口，将浏览器代理设置127.0.0.1:8080即可使用！！！")
    main()
