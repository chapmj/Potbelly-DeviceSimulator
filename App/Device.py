#!/usr/bin/python
import itertools
import time
from socket import socket, AF_INET, SOCK_STREAM
import select
import logging

logging.basicConfig(level=logging.DEBUG)

STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)


def byte_str(string):
    """Print each byte as a 2 digit base 16 value"""
    return " ".join("{:02X}".format(ord(c)) for c in string)


def calc_checksum(string):
    """
    Checksum is defined as the sum of bytes wrapped to 2 digits base 16.

    :returns: a string representation of the checksum
    """
    return bytes('%02X' % (sum(map(ord, string)) % 256))


class Device:
    """
    Simulates an ASTM1394 device sending and receiving messages.
    port: the port number for the device to open a connection
    messages: provide a test message tuple to export for testing.
    For example, an M record to test specimen location:
    ("1H|\^&", "2M|1|101|SID123456789|20201027235959|0", "3L|1|N")
    """
    def __init__(self, port, messages):
        self.sock = None
        self.conn = None
        self.port = port
        self.messages = messages

    @staticmethod
    def retry(func, tries):
        """Execute a method up to tries times"""
        tries = itertools.repeat(func, tries)

        for f in tries:
            is_success = f()
            if is_success:
                return True

        return False

    def create_socket(self, port):
        """Open a network socket"""

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(5)
        self.conn, addr = self.sock.accept()
        logging.debug("Device socket created")

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

    def send(self, data):
        """Wrapper for socket.send"""

        logging.debug("Write: [" + byte_str(data) + "]")
        self.conn.sendall(data)
        logging.debug("Sent: [" + data + "]")

    def send_enq(self, tries=1):
        """
        Sends ENQ characters to open a transaction.

        :returns: True if ENQ was acknowledged
        """

        if tries > 1:
            return Device.retry(self.send_enq, tries)

        else:
            data_received = ""

            while not data_received:
                self.send(ENQ)
                data_received = self.receive()

            logging.debug(data_received[0] == ACK)

            return data_received[0] == ACK

    def wait_enq(self, tries=1):
        """
        Listen for ENQs and respond with ACKs.

        :returns: True if ACK was sent
        """

        if tries > 1:
            return Device.retry(self.wait_enq, tries)

        else:
            logging.info("Waiting for ENQ")
            data_received = self.receive()

            if data_received and data_received[0] == ENQ:
                logging.debug("Got ENQ, sending ACK")
                self.send(ACK)
                return True

            if data_received and data_received[0] == ACK:
                logging.debug("Got ACK, sending ACK")
                return True

            return False

    def receive_message(self, tries):
        """
        Receive data until end of message character is found,
        returns true if entire message was received.

        :param tries: Max no. of times to execute this method
        :returns: True if a complete message is received
        """

        logging.info("Receiving data")

        if tries > 1:
            return Device.retry(self.receive_message, 3)

        else:

            while True:

                data_received = self.receive()
                logging.debug("Received: [" + byte_str(data_received) + "]")

                if data_received and data_received[0] == STX:
                    logging.debug(data_received)
                    self.send(ACK)
                    continue

                elif data_received and data_received[0] == EOT:
                    return True

                elif data_received:
                    continue

                else:
                    return False

    def send_message(self, message):
        """
        Sends message, wrapping with ctrl chars and checksum.

        :param message: A tuple or list of ASTM frames.
        :returns: None
        """

        logging.debug("Inside send_message")

        # Send every frame in the message, await ack per frame
        while message:

            checksum = calc_checksum(message[0] + CR + ETX)

            full_frame = STX + message[0] + CR + ETX + checksum + CR + LF

            self.send(full_frame)

            data_received = self.receive()

            if data_received and data_received[0] == ACK:
                message.pop(0)

        # End of transaction
        self.send(EOT)

    def close(self):
        self.sock.close()

    def receive_state(self):
        """
        Receives data.

        :returns: True if the state is completed, False if the data received is incomplete.
        """

        is_enq_received = self.wait_enq(3)
        is_msg_received = False

        if is_enq_received:
            logging.debug("ENQ received")
            is_msg_received = self.receive_message(3)

        if is_msg_received:
            logging.debug("Message received")

        is_state_complete = not is_msg_received

        return is_state_complete

    def send_state(self):

        if self.messages:
            logging.info("Sending...")

            while self.messages:
                is_enq_accepted = self.send_enq(3)
                if is_enq_accepted:
                    logging.info("Sending message...")
                    self.send_message(self.messages.pop(0))

                elif is_enq_accepted and not self.messages:
                    self.send(EOT)

        else:
            logging.info("No messages to send")

        is_state_complete = True

        return is_state_complete

    def run(self):
        """Cycles through states and loops until the process is killed"""

        states = itertools.cycle([(self.receive_state, "RECEIVE_STATE"), (self.send_state, "SEND_STATE")])
        state = states.next()

        logging.info("Starting...")
        self.create_socket(self.port)

        # Sleep necessary to prevent contention with client
        time.sleep(5)

        try:
            change_state = False
            while True:
                if change_state:
                    logging.debug("Changing run state")
                    logging.debug("Completed: " + state[1])
                    state = states.next()
                    logging.debug("New State: " + state[1])

                # Execute current state, signal if state is completed
                change_state = state[0]()

        except KeyboardInterrupt:
            self.close()
