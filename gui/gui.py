from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PyQt5.QtCore import QSize, QEventLoop, Qt, QTimer
from PyQt5.QtGui import QIcon, QTextCursor
from sys import argv, exit
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from random import randint
from time import time
from os import _exit
from ecies.utils import generate_eth_key
from ecies import encrypt, decrypt

class Window(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.setWindowTitle("dChat")
        self.setWindowIcon(QIcon('icons/icon.png'))
        self.setFixedSize(QSize(350, 300))
        layout = QVBoxLayout(self)

        self.textEdit = QTextEdit()
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Message")
        self.textEdit.setReadOnly(True)

        layout.addWidget(self.textEdit)
        layout.addWidget(self.lineEdit)

        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("", randint(1024, 49151)))
        self.timeout = 60
        self.ping = 0

        self.addr = "" # SERVER IP
        self.port = 1024

        self.addr_conn = ""
        self.port_conn = 0

        key = generate_eth_key()
        self.private_key = key.to_hex()
        self.public_key = key.public_key.to_hex()

        self.conn_pub_key = ""

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            message = self.lineEdit.text()
            if message != "" and message != "/ping":
                print("> " + message)
                self.textEdit.append("> " + message)
                message = message.encode()
                message = encrypt(self.conn_pub_key, message)
                message_chunks = list()
                for x in range(0, len(message), 2048):
                    message_chunks.append(message[x:x+2048])
                for elem in message_chunks:
                    self.sock.sendto(elem, (self.addr_conn, self.port_conn))
                self.timeout = 60
                self.lineEdit.setText("")
            if message == "/ping":
                self.textEdit.append(message)
                self.sock.sendto("cmd:{/ping-start}".encode(), (self.addr_conn, self.port_conn))
                self.ping = time()
                self.lineEdit.setText("")
        event.accept()

class HolePunching(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def run(self):
        window.sock.sendto(b'', (window.addr, window.port))

        (window.addr_conn, window.port_conn) = eval(window.sock.recvfrom(1024)[0].decode())
        print((window.addr_conn, window.port_conn))

        window.sock.sendto(b'', (window.addr_conn, window.port_conn))
        window.sock.sendto(f"pub-key:{{{window.public_key}}}".encode(), (window.addr_conn, window.port_conn))
        window.textEdit.append("<div style='color:#008000;'>[CONNECTED]</div>")
        window.textEdit.append("")
        window.lineEdit.setDisabled(False)
        window.lineEdit.setFocus()

class ServerThread(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def sleep(self, time):
        loop = QEventLoop()
        QTimer.singleShot(time, loop.quit)
        loop.exec_()

    def run(self):
        unw_msg = ["", "/ping", "cmd:{/ping-start}", "cmd:{/ping-end}"]
        while True:
            try:
                message = window.sock.recvfrom(2048)[0]
                try:
                    message = message.decode()
                    if message == "cmd:{/ping-start}":
                        window.sock.sendto("cmd:{/ping-end}".encode(), (window.addr_conn, window.port_conn))
                    if message == "cmd:{/ping-end}":
                        window.ping = time() - window.ping
                        window.textEdit.append(f"{round(window.ping, 4) * 1000} ms")
                        window.textEdit.moveCursor(QTextCursor.End)
                        window.ping = 0
                    if "pub-key:{" in message:
                        print("Key received")
                        window.conn_pub_key = message[9:-1]
                except UnicodeDecodeError:
                    message = decrypt(window.private_key, message).decode()
                    print("< " + message)
                    window.textEdit.append("< " + message)
                    window.textEdit.moveCursor(QTextCursor.End)
            except ConnectionResetError:
                window.textEdit.append("<div style='color:#ff0000;'>[DISCONNECTED]</div>")
                window.textEdit.append("<b>Exit in 30 seconds</b>")
                window.lineEdit.setDisabled(True)
                self.sleep(1000 * 30)
                _exit(0)

class ConnSupport(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window = window

    def sleep(self, time):
        loop = QEventLoop()
        QTimer.singleShot(time, loop.quit)
        loop.exec_()

    def run(self):
        while True:
            if window.timeout == 0:
                window.sock.sendto(b'', (window.addr_conn, window.port_conn))
                window.timeout = 60
            self.sleep(1000)
            window.timeout -= 1

if __name__ == "__main__":
    app = QApplication(argv)

    window = Window(app)
    window.show()
    window.textEdit.append("<div style='color:#808080;'>[CONNECTING]</div>")
    window.lineEdit.setDisabled(True)

    holePunching = HolePunching(window)
    holePunching.daemon = True
    holePunching.start()

    serverThread = ServerThread(window)
    serverThread.daemon = True
    serverThread.start()

    connSupport = ConnSupport(window)
    connSupport.daemon = True
    connSupport.start()

    exit(app.exec_())
