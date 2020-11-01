import sys

from Device import Device
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    messages = []

    if len(sys.argv) > 1:
        sample_id = sys.argv[1]
        messages.append(["1H|\^&", "2M|1|101|" + sample_id + "|20201027235959|0", "3L|1|N"])

    device = Device(6001, messages)
    device.run()