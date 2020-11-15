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

        while message:
            checksum = calc_checksum(message[0] + CR + ETX)  # Separate into a dependency
            full_frame = STX + message[0] + CR + ETX + checksum + CR + LF  # Separate into a dependency
            framed_message.append(full_frame)
            message.pop(0)

        return framed_message
