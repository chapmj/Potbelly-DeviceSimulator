#!/usr/bin/python
import itertools
import time
import logging

logging.basicConfig(level=logging.DEBUG)

STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)


class Device:
    """
    Simulates an ASTM1394 device sending and receiving messages.
    port: the port number for the device to open a connection
    messages: provide a test message tuple to export for testing.
    For example, an M record to test specimen location:
    ("1H|\^&", "2M|1|101|SID123456789|20201027235959|0", "3L|1|N")
    """

    def __init__(self, socket_server, frame_prepper, messages):
        self.socket_server = socket_server
        self.messages = messages
        self.frame_prepper = frame_prepper

    @staticmethod
    def retry(func, tries):
        """Execute a method up to tries times"""
        tries = itertools.repeat(func, tries)

        for f in tries:
            is_success = f()
            if is_success:
                return True

        return False

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
                self.socket_server.send(ENQ)
                data_received = self.socket_server.receive()

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
            data_received = self.socket_server.receive()

            if data_received and data_received[0] == ENQ:
                logging.debug("Got ENQ, sending ACK")
                self.socket_server.send(ACK)
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

        while True:

            data_received = self.socket_server.receive()

            if data_received and data_received[0] == STX:
                logging.debug(data_received)
                self.socket_server.send(ACK)
                continue

            elif data_received and data_received[0] == EOT:
                return True

            elif data_received:
                continue

            else:
                return False

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

            framed_message = self.frame_prepper(self.messages[0])

            is_enq_accepted = self.send_enq(3)
            if is_enq_accepted:
                logging.info("Sending message...")

                # Send every frame in the message, wait for ack per frame
                logging.debug("Inside send_message")
                while framed_message:

                    self.socket_server.send(framed_message[0])

                    data_received = self.socket_server.receive()

                    if data_received and data_received[0] == ACK:
                        framed_message.pop(0)

                self.socket_server.send(EOT)

        else:
            logging.info("No messages to send")

        is_state_complete = True

        return is_state_complete

    def run(self):
        """Cycles through states and loops until the process is killed"""

        states = itertools.cycle([(self.receive_state, "RECEIVE_STATE"), (self.send_state, "SEND_STATE")])
        state = states.next()

        logging.info("Starting...")
        self.socket_server.start()

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
                change_state = apply(state[0])

        except KeyboardInterrupt:
            self.socket_server.stop()
