from unittest import TestCase

from pylsqpack import Decoder, Encoder, StreamBlocked


class RoundtripTest(TestCase):
    def test_cancel_stream(self):
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0

        # apply decoder settings
        encoder.apply_settings(0x100, 0x10)

        # encode headers twice so the second block uses the dynamic table
        encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        control, data = encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        self.assertEqual(control, b"b=E\x82\x94\xe7Ctwo\x03bar")

        # the stream is blocked as the encoder stream data was not received
        with self.assertRaises(StreamBlocked):
            decoder.feed_header(stream_id, data)

        # cancel the stream, the encoder accepts the instruction
        cancel = decoder.cancel_stream(stream_id)
        self.assertEqual(cancel, b"\x40")
        encoder.feed_decoder(cancel)

        # the decoder no longer reports the stream as unblocked
        self.assertEqual(decoder.feed_encoder(control), [])

    def test_simple(self):
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0

        # encode headers
        control, data = encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        self.assertEqual(control, b"")
        self.assertEqual(data, b"\x00\x00*=E\x82\x94\xe7#two\x03bar")

        # decode headers
        decoder.feed_encoder(control)
        control, headers = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"")
        self.assertEqual(headers, [(b"one", b"foo"), (b"two", b"bar")])

    def test_with_settings(self):
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0

        # apply decoder settings
        tsu = encoder.apply_settings(0x100, 0x10)
        self.assertEqual(tsu, b"\x3f\xe1\x01")

        # ROUND 1

        # encode headers
        control, data = encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        self.assertEqual(control, b"")
        self.assertEqual(data, b"\x00\x00*=E\x82\x94\xe7#two\x03bar")

        # decode headers
        decoder.feed_encoder(control)
        control, headers = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"")
        self.assertEqual(headers, [(b"one", b"foo"), (b"two", b"bar")])

        # ROUND 2

        # encode headers
        control, data = encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        self.assertEqual(control, b"b=E\x82\x94\xe7Ctwo\x03bar")
        self.assertEqual(data, b"\x03\x81\x10\x11")

        # decode headers
        decoder.feed_encoder(control)
        control, headers = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"\x80")
        self.assertEqual(headers, [(b"one", b"foo"), (b"two", b"bar")])

        # ROUND 3

        # encode headers
        control, data = encoder.encode(stream_id, [(b"one", b"foo"), (b"two", b"bar")])
        self.assertEqual(control, b"")
        self.assertEqual(data, b"\x03\x00\x81\x80")

        # decode headers
        decoder.feed_encoder(control)
        control, headers = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"\x80")
        self.assertEqual(headers, [(b"one", b"foo"), (b"two", b"bar")])
