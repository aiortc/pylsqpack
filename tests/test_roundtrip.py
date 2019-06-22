from unittest import TestCase

from pylsqpack import Decoder, Encoder


class RoundtripTest(TestCase):
    def test_simple(self):
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0
        seqno = 0

        # encode headers
        control, data = encoder.encode(
            stream_id, seqno, [(b"one", b"foo"), (b"two", b"bar")]
        )
        self.assertEqual(control, b"")
        self.assertEqual(data, b"\x00\x00*=E\x82\x94\xe7#two\x03bar")

        # decode headers
        decoder.feed_control(control)
        control, headers = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"")
        self.assertEqual(headers, [(b"one", b"foo"), (b"two", b"bar")])
