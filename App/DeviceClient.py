import logging
import socket
import sys

STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)


class DeviceClient:
    """Mimics a consumer of device data.  It is a "client" per the network context"""

    def __init__(self, addr="127.0.0.1", port=6001):
        self.addr = addr
        self.port = port

    def run(self):
        logging.info('Creating socket at ' + self.addr + " " + str(self.port))

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        except socket.error:
            logging.error('Failed to create socket')
            sys.exit()

        s.connect((self.addr, self.port))

        while True:

            reply = s.recv(4096)

            if reply:
                if reply[0] == ENQ:
                    logging.info("ENQ -> ACK")
                    s.sendall(ACK)

                if reply[0] == STX:
                    logging.info("STX -> ACK")
                    logging.debug(reply)
                    s.sendall(ACK)

                if reply[0] == EOT:
                    logging.info("-EOT-")
