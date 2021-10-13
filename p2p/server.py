from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

def server():
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("", 1024))

    adresses = []

    while True:
        message = sock.recvfrom(1024)
        print(message[1], "<<< \33[32m[CONNECTED]\33[0m")
        if not message[1] in adresses:
            adresses.append(message[1])
        if len(adresses) == 2:
            sock.sendto(str(adresses[0]).encode(), adresses[1])
            sock.sendto(str(adresses[1]).encode(), adresses[0])
            adresses = []
            print("")

def exit():
    while True:
        cmd = input()
        if cmd == "exit":
            break

Thread(target=server, daemon=True).start()
Thread(target=exit).start()
