import logging
from socket import socket, AF_INET, SOCK_STREAM

import select


def byte_str(string):
    """Print each byte as a 2 digit base 16 value"""
    return " ".join("{:02X}".format(ord(c)) for c in string)


class SocketClient:
    def __init__(self, addr, port):
        self.port = port
        self.addr = addr
        self.sock = None
        self.conn = None
        self.is_open = False

    def start(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        logging.debug("Socket created")

        self.sock.connect((self.addr, self.port))
        logging.debug("Socket Connected")
        self.is_open = True

        logging.debug("Device socket created")

    def stop(self):
        self.sock.close()
        self.is_open = False

    def send(self, data):
        logging.debug("Write: [" + byte_str(data) + "]")
        self.sock.sendall(data)
        logging.debug("Sent: [" + data + "]")

    def receive(self):
        """
        Read data from socket.

        :returns data if exists, otherwise empty string
        """

        logging.debug("Inside receive")
        data = ""

        ready = select.select([self.sock], [], [], float(5))

        if ready[0]:
            logging.debug("Connection has data")
            data = self.sock.recv(4096)

        if data:
            logging.debug("Read: [" + byte_str(data) + "]")
            logging.debug("Received: [ " + data + "]")

        return data
