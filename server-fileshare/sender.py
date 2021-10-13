from socket import socket, AF_INET, SOCK_STREAM
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("filepath", type=str)
args = parser.parse_args()

send_filepath = args.filepath

HOST = "" # SERVER IP
PORT = 1024

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((HOST, PORT))

filename = send_filepath.split("/")[-1]
sock.send(filename.encode())

file = open(send_filepath, "rb")

print(f"Sending {filename}...")
data = file.read(1024)
while data:
    sock.send(data)
    data = file.read(1024)
file.close()
print("Done Sending")

sock.close()
