from unittest import TestCase

from pylsqpack import Decoder, Encoder, FieldSectionTooLarge, StreamBlocked


class RoundtripTest(TestCase):
    def test_cancel_stream(self) -> None:
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

    def test_field_section_too_large(self) -> None:
        """
        After a header block is refused for exceeding the maximum field section
        size, the decoder cancels the stream and keeps decoding header blocks
        which use the dynamic table, in step with the encoder.
        """
        encoder = Encoder()
        # (3 + 3 + 32) + (3 + 3 + 32) = 76 bytes, so headers fit but not twice.
        decoder = Decoder(0x100, 0x10, max_field_section_size=100)
        headers = [(b"one", b"foo"), (b"two", b"bar")]

        # apply decoder settings
        encoder.apply_settings(0x100, 0x10)

        # ROUND 1: the headers are sent as literals
        control, data = encoder.encode(0, headers)
        self.assertEqual(control, b"")
        self.assertEqual(decoder.feed_header(0, data), (b"", headers))

        # ROUND 2: the headers are inserted into the dynamic table, then
        # referenced twice, which exceeds the limit
        control, data = encoder.encode(4, headers * 2)
        self.assertEqual(control, b"b=E\x82\x94\xe7Ctwo\x03bar")
        self.assertEqual(data, b"\x03\x81\x10\x11\x10\x11")
        self.assertEqual(decoder.feed_encoder(control), [])
        with self.assertRaises(FieldSectionTooLarge):
            decoder.feed_header(4, data)

        # the stream is cancelled, the encoder accepts the instruction
        cancel = decoder.cancel_stream(4)
        self.assertEqual(cancel, b"\x44")
        encoder.feed_decoder(cancel)

        # ROUND 3: the headers reference the dynamic table entries, and the
        # encoder accepts the acknowledgment
        control, data = encoder.encode(8, headers)
        self.assertEqual(control, b"")
        self.assertEqual(data, b"\x03\x00\x81\x80")
        control, decoded = decoder.feed_header(8, data)
        self.assertEqual(control, b"\x88")
        self.assertEqual(decoded, headers)
        encoder.feed_decoder(control)

    def test_large_headers(self) -> None:
        # Regression test for #57: the encoder used to write the header block
        # into a fixed 4 kB buffer, and reject any header whose name and value
        # exceeded 4 kB. Headers such as large cookies made encoding fail.
        encoder = Encoder()
        decoder = Decoder(0x100, 0x10)
        stream_id = 0
        headers = [
            (b"cookie", b"a" * 3548),
            (b"x-custom", b"b" * 1738),
            (b"x-large", b"c" * 20000),
        ]

        # encode headers, the header block buffer must grow well beyond 4 kB:
        # even after Huffman coding the values take 2218 + 1304 + 12500 bytes
        control, data = encoder.encode(stream_id, headers)
        self.assertEqual(control, b"")
        self.assertEqual(len(data), 16048)

        # decode headers
        decoder.feed_encoder(control)
        control, decoded = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"")
        self.assertEqual(decoded, headers)

    def test_large_headers_with_settings(self) -> None:
        # Regression test for #57: when the dynamic table is enabled, inserting
        # a large header produces encoder stream data, which the encoder used
        # to write into a separate fixed 4 kB buffer.
        encoder = Encoder()
        decoder = Decoder(0x4000, 0x10)
        stream_id = 0
        headers = [(b"x-large", b"c" * 8000)]

        # apply decoder settings
        encoder.apply_settings(0x4000, 0x10)

        # ROUND 1

        # encode headers, the header has not been seen before so it is sent as
        # a literal in the header block, and the encoder stream is empty
        control, data = encoder.encode(stream_id, headers)
        self.assertEqual(control, b"")
        self.assertEqual(len(data), 5012)

        # decode headers
        decoder.feed_encoder(control)
        control, decoded = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"")
        self.assertEqual(decoded, headers)

        # ROUND 2

        # encode headers, the header has been seen before so it is inserted
        # into the dynamic table: the encoder stream buffer must grow beyond
        # 4 kB, while the header block only holds a reference to the entry
        control, data = encoder.encode(stream_id, headers)
        self.assertEqual(len(control), 5010)
        self.assertEqual(data, b"\x02\x80\x10")

        # decode headers
        decoder.feed_encoder(control)
        control, decoded = decoder.feed_header(stream_id, data)
        self.assertEqual(control, b"\x80")
        self.assertEqual(decoded, headers)

    def test_simple(self) -> None:
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

    def test_with_settings(self) -> None:
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
