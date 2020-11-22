from .SocketClient import SocketClient
from .SocketServer import SocketServer


def get_client(addr, port):
    return SocketClient(addr, port)


def get_server(port):
    return SocketServer(port)
