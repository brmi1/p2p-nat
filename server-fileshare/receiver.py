from socket import socket, AF_INET, SOCK_STREAM

HOST = ""
PORT = 1024

sock = socket(AF_INET, SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

conn, addr = sock.accept()

recv_file = conn.recv(1024).decode()
file = open(recv_file, "wb")

print(f"Receiving {recv_file}...")
data = conn.recv(1024)
while data:
    file.write(data)
    data = conn.recv(1024)
file.close()
print("Done Receiving")

conn.close()
sock.close()
