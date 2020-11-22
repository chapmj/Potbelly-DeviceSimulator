from FramePrepper import FramePrepper

STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
ETB = chr(0x17)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)


def calc_checksum(string):
    """
    Checksum is defined as the sum of bytes wrapped to 2 digits base 16.

    :returns: a string representation of the checksum
    """
    return bytes('%02X' % (sum(map(ord, string)) % 256))


class FramePrepperSimpleETX(FramePrepper):

    def prepare_frames(self, message):

        if not message:
            return None

        # Wrap message in control characters
        framed_message = []

        indexed_messages = [frame for frame in self.index_frames(message)]

        crd_messages = [frame + CR for frame in indexed_messages]

        for message in crd_messages:
            checksum = calc_checksum(message + ETX)
            full_frame = STX + message + ETX + checksum + CR + LF
            framed_message.append(full_frame)

        return framed_message

    # indexed_message = [frame for frame in self.index_frames(message)]
    def index_frames(self, message):
        index = 1
        for frame in message:
            frame = str(index) + frame
            index = (index + 1) % 8
            yield frame


if __name__ == "__main__":
    prepper = FramePrepperSimpleETX()
    test_frames = prepper.prepare_frames(["abc", "def", "ghi", "jkl", "mno", "pqr", "stu", "vwx", "yz"])
    print(test_frames)
