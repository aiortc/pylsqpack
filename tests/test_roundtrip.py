from unittest import TestCase

from pylsqpack import Decoder, Encoder


class RoundtripTest(TestCase):
    def test_simple(self):
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0
        seqno = 0

        control, header = encoder.encode(
            stream_id, seqno, [(b"one", b"foo"), (b"two", b"bar")]
        )

        decoder.feed_control(control)
        self.assertEqual(
            decoder.feed_header(stream_id, header), [(b"one", b"foo"), (b"two", b"bar")]
        )
