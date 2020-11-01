import logging
from sys import (argv, exit)

from DeviceClient import DeviceClient

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    addr = ""
    port = 0

    if len(argv) > 3:
        logging.error("Too many args.  Usage: App-client.py [address] [port]")
        exit()

    elif len(argv) > 2:
        addr = argv[1]
        port = argv[2]

    elif len(argv) > 1:
        addr = argv[1]

    else:
        addr = "127.0.0.1"
        port = 6001

    logging.info("Creating client to " + addr + " " + str(port))
    client = DeviceClient(addr, port)

    client.run()
