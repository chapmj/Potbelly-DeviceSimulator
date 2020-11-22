import logging
from socket import socket, AF_INET, SOCK_STREAM

import select


def byte_str(string):
    """Print each byte as a 2 digit base 16 value"""
    return " ".join("{:02X}".format(ord(c)) for c in string)


class SocketServer:
    def __init__(self, port):
        self.port = port
        self.sock = None
        self.conn = None

    def start(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            logging.debug("Socket created")
            self.sock.bind(('', self.port))
            logging.debug("Socket bound")
            self.sock.listen(5)
            logging.debug("Socket listening")
            self.conn, addr = self.sock.accept()
            logging.debug("Socket accepted")
            logging.debug("Device socket created")

        except KeyboardInterrupt:
            logging.error("KeyboardInterrupt")

    def stop(self):
        self.sock.close()

    def send(self, data):
        logging.debug("Write: [" + byte_str(data) + "]")
        self.conn.sendall(data)
        logging.debug("Sent: [" + data + "]")
        pass

    def receive(self):
        """
        Read data from socket.

        :returns data if exists, otherwise empty string
        """

        logging.debug("Inside receive")
        data = ""

        ready = select.select([self.conn], [], [], 5)

        if ready[0]:
            logging.debug("Connection has data")
            data = self.conn.recv(4096)

        if data:
            logging.debug("Read: [" + byte_str(data) + "]")
            logging.debug("Received: [ " + data + "]")

        return data
