from unittest import TestCase

from pylsqpack import DecoderStreamError, Encoder


class EncoderTest(TestCase):
    def test_decoder_stream_error(self):
        encoder = Encoder()
        with self.assertRaises(DecoderStreamError) as cm:
            encoder.feed_decoder(b"\x00")
        self.assertEqual(str(cm.exception), "lsqpack_enc_decoder_in failed")

    def test_encode_not_a_tuple(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, ["hello"])
        self.assertEqual(str(cm.exception), "the header must be a two-tuple")

    def test_encode_name_empty(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(b"", b"bar")])
        self.assertEqual(str(cm.exception), "the header's name must not be empty")

    def test_encode_name_not_bytes(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(1, b"bar")])
        self.assertEqual(str(cm.exception), "the header's name and value must be bytes")

    def test_encode_value_not_bytes(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(b"foo", 1)])
        self.assertEqual(str(cm.exception), "the header's name and value must be bytes")

    def test_encode_name_too_long(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(bytes(65536), bytes(1))])
        self.assertEqual(str(cm.exception), "the header's name is too long")

    def test_encode_value_too_long(self):
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(bytes(1), bytes(65536))])
        self.assertEqual(str(cm.exception), "the header's value is too long")

    def test_encode_max_length(self):
        encoder = Encoder()
        stream_id = 0
        encoder.encode(stream_id, [(bytes(65535), bytes(65535))])
