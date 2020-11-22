from FramePrepper import FramePrepper

# Standard control chars
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


class FramePrepperBlob(FramePrepper):
    """
        Format a message into evenly sized chunks, wrapping each chunk with transmission chars and checksum
    """

    def prepare_frames(self, message, chunk_sz=239):
        """
        Wrap message in control characters

        :param message:   List of message frames
        :param chunk_sz:  Size of chunks to divide message into
        :return:    Fully formatted message, ready to send
        """
        # todo efficiency: lots of loops, but separated for clarity

        # Append CR to every message
        crd_messages = [msg_frame + CR for msg_frame in message]

        # Combine message into one string
        blob = ""
        for component in crd_messages:
            blob = blob + component

        # Divide string into chunks, per device interface specification
        unframed_message = [chunk for chunk in self.split_by_size(blob, chunk_sz)]

        # Prefix each chunk with an index number
        indexed_message = [chunk for chunk in self.index_frames(unframed_message)]

        # Prefix, checksum, suffix
        framed_message = [chunk for chunk in self.frame_with_control_chars(indexed_message)]

        return framed_message

    def calc_checksum(self, string):
        """
        Checksum is defined as the sum of bytes wrapped to 2 digits base 16.

        :returns: a string representation of the checksum
        """
        return bytes('%02X' % (sum(map(ord, string)) % 256))

    def frame_with_control_chars(self, msg_parts):

        for count, msg in enumerate(msg_parts):
            prefix = STX

            if count == len(msg_parts):
                suffix = ETX
            else:
                suffix = ETB

            checksum = self.calc_checksum(msg + suffix)

            formatted_frame = prefix + msg + suffix + checksum + CR + LF

            yield formatted_frame

    def split_by_size(self, text, chunk_sz):

        num_chunks = len(text) // chunk_sz + (len(text) % chunk_sz > 0)

        for chunk_cnt in range(0, num_chunks):
            chunk_pos = chunk_sz * chunk_cnt
            chunk = text[chunk_pos: chunk_pos + chunk_sz]
            yield chunk

    def index_frames(self, message):
        index = 1
        for frame in message:
            frame = str(index) + frame
            index = (index + 1) % 8
            yield frame

if __name__ == "__main__":
    prepper = FramePrepperBlob()
    test_msgs = ["abcdef", "ghi", "jklmnopqrs", "tuvwxyz", "ABCDEF", "GHIJK", "LMNOP", "QRSTUVWXYZ", "p"]
    frames = prepper.prepare_frames(test_msgs, 7)
    for frame in frames:
        print(frame)
