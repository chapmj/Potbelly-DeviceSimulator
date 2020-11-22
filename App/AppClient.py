import logging
from sys import (argv, exit)

import Socket
from Device.DeviceClient import DeviceClient

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    addr = ""
    port = 0

    if len(argv) > 3:
        logging.error("Too many args.  Usage: App-client.py [address] [port]")
        exit()

    elif len(argv) > 2:
        print("here2")
        addr = argv[1]
        port = argv[2]

    elif len(argv) > 1:
        print(argv)
        addr = argv[1]
        addr = 6001

    else:
        addr = "127.0.0.1"
        port = 6001

    try:
        logging.info("Creating client to " + addr + " " + str(port))
        socket = Socket.get_client(addr, port)
        logging.debug("Got socket")
        client = DeviceClient(socket)
        logging.debug("Got deviceclient")
        client.run()

    except KeyboardInterrupt:
        logging.error('KeyboardQuit')
