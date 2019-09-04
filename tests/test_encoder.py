from unittest import TestCase

from pylsqpack import DecoderStreamError, Encoder


class EncoderTest(TestCase):
    def test_decoder_stream_error(self):
        encoder = Encoder()
        with self.assertRaises(DecoderStreamError) as cm:
            encoder.feed_decoder(b"\x00")
        self.assertEqual(str(cm.exception), "lsqpack_enc_decoder_in failed")
