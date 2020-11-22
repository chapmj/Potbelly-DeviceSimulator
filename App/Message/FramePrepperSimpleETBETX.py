from FramePrepper import FramePrepper

# STX = chr(0x2)
# ETX = chr(0x3)
# ENQ = chr(0x5)
# ACK = chr(0x6)
# ETB = chr(0x17)
# EOT = chr(0x4)
# CR = chr(0xD)
# LF = chr(0xA)

# Printable characters for debugging
STX = "$"
ETX = "@"
ETB = "#"
CR = "^"
LF = "&"


def calc_checksum(string):
    """
    Checksum is defined as the sum of bytes wrapped to 2 digits base 16.

    :returns: a string representation of the checksum
    """
    return bytes('%02X' % (sum(map(ord, string)) % 256))


class FramePrepperSimpleETBETX(FramePrepper):

    def prepare_frames(self, message):
        # Wrap message in control characters
        framed_message = []

        indexed_messages = [frame for frame in self.index_frames(message)]

        crd_messages = [frame + CR for frame in indexed_messages]

        for count, message in enumerate(crd_messages):
            if count + 1 == len(crd_messages):
                print("end")
                suffix = ETX
            else:
                suffix = ETB

            checksum = calc_checksum(message + suffix)
            full_frame = STX + message + suffix + checksum + CR + LF
            framed_message.append(full_frame)

        return framed_message

    def index_frames(self, message):
        index = 1
        for frame in message:
            frame = str(index) + frame
            index = (index + 1) % 8
            yield frame


if __name__ == "__main__":
    prepper = FramePrepperSimpleETBETX()
    test_frames = prepper.prepare_frames(["abc", "def", "ghi", "jkl", "mno", "pqr", "stu", "vwx", "yz"])
    for test_frame in test_frames:
        print(test_frame)
