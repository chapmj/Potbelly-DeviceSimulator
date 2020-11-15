from FramePrepper import FramePrepper

# Standard control chars
STX = chr(0x2)
ETX = chr(0x3)
ENQ = chr(0x5)
ACK = chr(0x6)
ETB = chr(0x17)
EOT = chr(0x4)
CR = chr(0xD)
LF = chr(0xA)

# Printable characters for debugging
#STX = "$"
#ETX = "@"
#ETB = "#"
#CR = "^"


class FramePrepperBlob(FramePrepper):
    """
        Format a message into evenly sized chunks, wrapping each chunk with transmission chars and checksum
    """

    def prepare_frames(self, message, chunk_sz = 240):
        # Wrap message in control characters
        framed_message = []
        blob = ""
        for part in message:
            blob = blob + part + CR

        unframed_message = [frame for frame in self.split_by_size(blob, chunk_sz)]
        framed_message = [frame for frame in self.frame_with_control_chars(unframed_message)]

        return framed_message

    def calc_checksum(self, string):
        """
        Checksum is defined as the sum of bytes wrapped to 2 digits base 16.

        :returns: a string representation of the checksum
        """
        return bytes('%02X' % (sum(map(ord, string)) % 256))

    def frame_with_control_chars(self, msg_parts):

        for count, msg in enumerate(msg_parts):
            if count == len(msg_parts):
                frame = STX + str(count % 8) + msg + self.calc_checksum(msg) + ETX
                yield frame
            else:
                frame = STX + str(count % 8) + msg + self.calc_checksum(msg) + ETB
                yield frame

    def split_by_size(self, text, chunk_sz):
        num_chunks = len(text) // chunk_sz + (len(text) % chunk_sz > 0)
        for chunk_cnt in range(0, num_chunks):

            chunk_pos = chunk_sz * chunk_cnt

            chunk = text[chunk_pos : chunk_pos + chunk_sz]
            yield chunk


if __name__ == "__main__":
    prepper = FramePrepperBlob()
    msg = ["abcdef", "ghi", "jklmnopqrs", "tuvwxyz", "ABCDEF", "GHIJK", "LMNOP", "QRSTUVWXYZ"]
    chunks = prepper.prepare_frames(msg, 5)
    for part in chunks:
        print(part)