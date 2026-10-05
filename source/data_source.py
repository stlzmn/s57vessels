# data source classes for socket and serial connections
# author: Łukasz Stolzmann

import serial
import pyodbc
import threading
from socket import socket, AF_INET, SOCK_STREAM

class LazySocketConn:
    def __init__(self, address, port, family=AF_INET, conn_type=SOCK_STREAM):
        self.address = address
        self.port = port
        self.family = family
        self.conn_type = conn_type
        self.local = threading.local()
    
    def readline(self):
        line = ''
        while (char := self.local.sock.recv(1).decode('utf-8')) != '\n':
            line += char
        return line

    def __enter__(self):
        if hasattr(self.local, 'sock'):
            raise RuntimeError('Połączenie jest już nawiązane.')
        self.local.sock = socket(self.family, self.conn_type)
        self.local.sock.connect((self.address, self.port))
        return self
    
    def __exit__(self, exec_ty, exec_val, tb):
        self.local.sock.close()
        del self.local.sock

class SerialInput:
    def __init__(self, port='COM1', baudrate=4800, timeout=0, parity=serial.PARITY_NONE, rtscts=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.rtscts = rtscts
        self.local = threading.local()

    def readline(self):
        line = ''
        while (char := self.local.serial.read().decode('utf-8')) != '\n':
            line += char
        return line

    def __enter__(self):
        if hasattr(self.local, 'serial'):
            raise RuntimeError('Połączenie jest już nawiązane.')
        self.local.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout, parity=self.parity, rtscts=self.rtscts)
        return self
    
    def __exit__(self, exec_ty, exec_val, tb):
        self.local.serial.close()
        del self.local.serial

class CollzoneDatabaseConnection:
    def __init__(self, connection_name):
        self._connection_name = connection_name

    def __enter__(self):
        if hasattr(self, 'connection'):
            raise RuntimeError('Połączenie jest już nawiązane.')
        try:
            self.connection = pyodbc.connect(self._connection_name, timeout=1)
            self.cursor = self.connection.cursor()
        except:
            raise ConnectionError(f'Nie udało się połączyć z bazą {self._connection_name}')
        else:
            return self

    def __exit__(self, exec_ty, exec_val, tb):
        self.connection.close()
        del self.connection






