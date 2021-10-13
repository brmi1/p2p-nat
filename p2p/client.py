from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import time, sleep

addr = "" # SERVER IP
port = 1024
timeout = 60

sock = socket(AF_INET, SOCK_DGRAM)
sock.sendto(b'', (addr, port))

(addr_conn, port_conn) = eval(sock.recvfrom(1024)[0].decode())
print((addr_conn, port_conn))

sock.sendto(b'', (addr_conn, port_conn))

def client(timeout):
    while True:
        message = input(">>> ")
        sock.sendto(message.encode(), (addr_conn, port_conn))
        timeout = 60
        if message == "/ping":
            sock.sendto("cmd:{/ping-start}".encode(), (addr_conn, port_conn))
            global time_ping
            time_ping = time()

def server():
    unw_msg = ["", "/ping", "cmd:{/ping-start}", "cmd:{/ping-end}"]
    while True:
        message = sock.recvfrom(1024)[0].decode()
        if not message in unw_msg:
            print("\n<<<", message)
        if message == "cmd:{/ping-start}":
            sock.sendto("cmd:{/ping-end}".encode(), (addr_conn, port_conn))
        if message == "cmd:{/ping-end}":
            ping = time() - time_ping
            print(f"{round(ping, 4) * 1000} ms")

def conn_supp(timeout):
    while True:
        if timeout == 0:
            sock.sendto(b'', (addr_conn, port_conn))
            timeout = 60
        sleep(1)
        timeout -= 1

Thread(target=client, args=(timeout,)).start()
Thread(target=server).start()
Thread(target=conn_supp, args=(timeout,)).start()
