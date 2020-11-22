import sys

import Socket
from Message.SampleQuery import SampleQuery
from Message.FramePrepperSimpleETX import FramePrepperSimpleETX
from Device.Device import Device
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    messages = []

    if len(sys.argv) > 1:
        sample_id = sys.argv[1]
        sample_query_transaction = SampleQuery(sys.argv[1]).create_transaction()
        messages.append(sample_query_transaction)

    socket = Socket.get_server(6001)

    device = Device(socket, FramePrepperSimpleETX(), messages)

    try:
        device.run()
    except KeyboardInterrupt:
        logging.error('KeyboardQuit')
