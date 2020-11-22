import logging
import time

STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)

char_map = {
    STX: "<STX>",
    ETX: "<ETX>",
    CR: "<CR>",
    LF: "<LF>",
    ENQ: "<ENQ>",
    ACK: "<ACK>",
    EOT: "<EOT>"
}


class DeviceClient:
    """Mimics a consumer of device data.  It is a "client" per the network context"""

    def __init__(self, socket):
        self.socket = socket

    def run(self):
        self.socket.start()

        while self.socket.is_open:

            reply = self.socket.receive()
            human_reply = ""

            if reply:
                if reply[0] == ENQ:
                    logging.info("ENQ -> ACK")
                    self.socket.send(ACK)

                if reply[0] == STX:
                    logging.info("STX -> ACK")

                    for b in reply:
                        if b in char_map:
                            human_reply += char_map.get(b)
                        else:
                            human_reply += b

                    logging.debug(human_reply)

                    self.socket.send(ACK)

                if reply[0] == EOT:
                    logging.info("-EOT-")

            else:
                time.sleep(1)
                logging.debug("No data")

        self.socket.stop()
