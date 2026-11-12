from unittest import TestCase

from pylsqpack import DecoderStreamError, Encoder


class EncoderTest(TestCase):
    def test_apply_settings(self) -> None:
        """
        The encoder accepts any value the decoder's settings can carry, and uses
        a dynamic table of at most 4096 bytes whatever the decoder allows.
        """
        for args, control in [
            ((0, 0), b""),
            ((0x100, 0x10), b"\x3f\xe1\x01"),
            ((4096, 0x10), b"\x3f\xe1\x1f"),
            ((65536, 0x10), b"\x3f\xe1\x1f"),
            ((2**32, 2**32), b"\x3f\xe1\x1f"),
            ((2**62 - 1, 2**62 - 1), b"\x3f\xe1\x1f"),
        ]:
            with self.subTest(args=args):
                self.assertEqual(Encoder().apply_settings(*args), control)

    def test_apply_settings_blocked_streams(self) -> None:
        """
        The encoder risks blocking a stream, by referring to an entry which the
        decoder has not acknowledged, only if the decoder allows blocked streams.
        """
        headers = [(b"x-n", b"1")] * 2
        for blocked_streams, encoded in [
            (0, (b"", b"\x00\x00#x-n\x011#x-n\x011")),
            (1, (b"Cx-n\x011", b"\x02\x80#x-n\x011\x10")),
            (2**32, (b"Cx-n\x011", b"\x02\x80#x-n\x011\x10")),
        ]:
            with self.subTest(blocked_streams=blocked_streams):
                encoder = Encoder()
                encoder.apply_settings(4096, blocked_streams)
                self.assertEqual(encoder.encode(0, headers), encoded)

    def test_apply_settings_invalid_arguments(self) -> None:
        """
        The settings must be QUIC variable-length integers.
        """
        for args, message in [
            ((-1, 16), "max_table_capacity must be between 0 and 2**62 - 1"),
            ((2**62, 16), "max_table_capacity must be between 0 and 2**62 - 1"),
            ((4096, -1), "blocked_streams must be between 0 and 2**62 - 1"),
            ((4096, 2**62), "blocked_streams must be between 0 and 2**62 - 1"),
        ]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError) as cm:
                    Encoder().apply_settings(*args)
                self.assertEqual(str(cm.exception), message)

    def test_decoder_stream_error(self) -> None:
        encoder = Encoder()
        with self.assertRaises(DecoderStreamError) as cm:
            encoder.feed_decoder(b"\x00")
        self.assertEqual(str(cm.exception), "lsqpack_enc_decoder_in failed")

    def test_decoder_stream_not_bytes(self) -> None:
        encoder = Encoder()
        with self.assertRaises(TypeError):
            encoder.feed_decoder("hello")  # type: ignore[arg-type]

    def test_encode_not_a_list(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, ((b"foo", b"bar"),))  # type: ignore[arg-type]
        self.assertEqual(str(cm.exception), "headers must be a list")

    def test_encode_not_a_tuple(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, ["hello"])  # type: ignore[list-item]
        self.assertEqual(str(cm.exception), "the header must be a two-tuple")

    def test_encode_name_empty(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(b"", b"bar")])
        self.assertEqual(str(cm.exception), "the header's name must not be empty")

    def test_encode_name_not_bytes(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(1, b"bar")])  # type: ignore[list-item]
        self.assertEqual(str(cm.exception), "the header's name and value must be bytes")

    def test_encode_stream_id_invalid(self) -> None:
        """
        Stream IDs must be QUIC stream IDs, see RFC 9000 section 2.1.
        """
        encoder = Encoder()
        encoder.encode(2**62 - 1, [(b"foo", b"bar")])

        for stream_id in (-1, 2**62):
            with self.subTest(stream_id=stream_id):
                with self.assertRaises(ValueError) as cm:
                    encoder.encode(stream_id, [(b"foo", b"bar")])
                self.assertEqual(
                    str(cm.exception), "stream_id must be between 0 and 2**62 - 1"
                )

    def test_encode_value_not_bytes(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(b"foo", 1)])  # type: ignore[list-item]
        self.assertEqual(str(cm.exception), "the header's name and value must be bytes")

    def test_encode_name_too_long(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(bytes(65536), bytes(1))])
        self.assertEqual(str(cm.exception), "the header's name is too long")

    def test_encode_value_too_long(self) -> None:
        encoder = Encoder()
        stream_id = 0
        with self.assertRaises(ValueError) as cm:
            encoder.encode(stream_id, [(bytes(1), bytes(65536))])
        self.assertEqual(str(cm.exception), "the header's value is too long")

    def test_encode_max_length(self) -> None:
        encoder = Encoder()
        stream_id = 0
        encoder.encode(stream_id, [(bytes(65535), bytes(65535))])

    def test_init_invalid_arguments(self) -> None:
        """
        The encoder takes no arguments: its settings are applied later.
        """
        for args, kwargs in [((4096,), {}), ((), {"max_table_capacity": 4096})]:
            with self.subTest(args=args, kwargs=kwargs):
                with self.assertRaises(TypeError):
                    Encoder(*args, **kwargs)
