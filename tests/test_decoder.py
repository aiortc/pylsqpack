import binascii
from unittest import TestCase

from pylsqpack import Decoder, StreamBlocked


class DecoderTest(TestCase):
    def test_blocked_stream(self):
        decoder = Decoder(0x100, 0x10)
        stream_id = 0

        # no streams unblocked
        self.assertEqual(decoder.feed_encoder(b""), [])

        # cannot resume non existent block
        with self.assertRaises(ValueError):
            decoder.resume_header(stream_id)

        # the stream is blocked
        with self.assertRaises(StreamBlocked):
            decoder.feed_header(stream_id, binascii.unhexlify("0482d9101112"))

        # the stream is still blocked
        with self.assertRaises(StreamBlocked):
            decoder.resume_header(stream_id)

        # the stream becomes unblocked
        self.assertEqual(
            decoder.feed_encoder(
                binascii.unhexlify(
                    "3fe10168f2b14939d69ce84f8d9635e9ef2a12bd454dc69a659f6cf2b14939d6"
                    "b505b161cc5a9385198fdad313c696dd6d5f4a082a65b6850400bea0837190dc"
                    "138a62d1bf"
                )
            ),
            [stream_id],
        )

        # the header is resumed
        control, headers = decoder.resume_header(stream_id)
        self.assertEqual(control, b"\x80")
        self.assertEqual(
            headers,
            [
                (b":status", b"200"),
                (b"x-echo-host", b"fb.mvfst.net:4433"),
                (b"x-echo-user-agent", b"aioquic"),
                (b"date", b"Sun, 21 Jul 2019 21:31:26 GMT"),
            ],
        )

        # free the decoder
        del decoder

    def test_invalid(self):
        decoder = Decoder(0x100, 0x10)

        with self.assertRaises(RuntimeError):
            decoder.feed_header(0, b"1")

    def test_blocked_stream_free(self):
        decoder = Decoder(0x100, 0x10)
        stream_id = 0

        # the stream is blocked
        with self.assertRaises(StreamBlocked):
            decoder.feed_header(stream_id, binascii.unhexlify("0482d9101112"))

        # free the decoder with pending block
        del decoder
