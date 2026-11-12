from collections.abc import Callable
from importlib import import_module
from typing import Any, TypeVar
from unittest import TestCase, skipIf

from pylsqpack import Decoder, Encoder, StreamBlocked

from .test_decoder import BIG_ENTRY_ENCODER, big_entry_references

try:
    _testcapi: Any = import_module("_testcapi")
except ImportError:
    _testcapi = None

T = TypeVar("T")
R = TypeVar("R")

BIG_ENTRY = (b"x-big", b"a" * 100)


def blocked_decoder() -> Decoder:
    """
    Return a decoder with a header block for stream 0 waiting for the entry
    inserted by BIG_ENTRY_ENCODER.
    """
    decoder = Decoder(4096, 16)
    try:
        decoder.feed_header(0, big_entry_references(2))
    except StreamBlocked:
        pass
    return decoder


def unblocked_decoder() -> Decoder:
    """
    Return a decoder with a header block for stream 0 ready to be resumed.
    """
    decoder = blocked_decoder()
    assert decoder.feed_encoder(BIG_ENTRY_ENCODER) == [0]
    return decoder


def filled_decoder() -> Decoder:
    """
    Return a decoder whose dynamic table holds the entry inserted by
    BIG_ENTRY_ENCODER.
    """
    decoder = Decoder(4096, 16)
    assert decoder.feed_encoder(BIG_ENTRY_ENCODER) == []
    return decoder


def primed_encoder() -> Encoder:
    """
    Return an encoder which inserts BIG_ENTRY into the dynamic table the next
    time it encodes it.
    """
    encoder = Encoder()
    encoder.apply_settings(4096, 16)
    encoder.encode(0, [BIG_ENTRY])
    return encoder


@skipIf(
    not hasattr(_testcapi, "set_nomemory"), "_testcapi.set_nomemory is not available"
)
class MemoryTest(TestCase):
    def assertSurvivesAllocationFailures(
        self, setup: Callable[[], T], call: Callable[[T], R], expected: R
    ) -> None:
        """
        Make the first allocation fail while running `call` on fresh state from
        `setup`, then only the second one, and so on, until enough calls in a row
        have succeeded to have gone past the last allocation.

        Each call must either raise MemoryError or return `expected`: it must not
        crash, nor return a result with an exception set, which CPython turns
        into a SystemError.
        """
        failures = successes = 0
        index = 0
        while successes < 20:
            state = setup()
            _testcapi.set_nomemory(index, index + 1)
            try:
                result = call(state)
            except MemoryError:
                result = None
            finally:
                _testcapi.remove_mem_hooks()

            if result is None:
                failures += 1
                successes = 0
            else:
                self.assertEqual(result, expected, f"allocation {index} failed")
                successes += 1
            index += 1
        self.assertGreater(failures, 0, "no allocation was made to fail")

    def test_decoder_feed_encoder(self) -> None:
        self.assertSurvivesAllocationFailures(
            blocked_decoder,
            lambda decoder: decoder.feed_encoder(BIG_ENTRY_ENCODER),
            [0],
        )

    def test_decoder_feed_header(self) -> None:
        self.assertSurvivesAllocationFailures(
            filled_decoder,
            lambda decoder: decoder.feed_header(0, big_entry_references(2)),
            (b"\x80", [BIG_ENTRY, BIG_ENTRY]),
        )

    def test_decoder_resume_header(self) -> None:
        self.assertSurvivesAllocationFailures(
            unblocked_decoder,
            lambda decoder: decoder.resume_header(0),
            (b"\x80", [BIG_ENTRY, BIG_ENTRY]),
        )

    def test_encoder_encode(self) -> None:
        expected = primed_encoder().encode(4, [BIG_ENTRY])
        self.assertNotEqual(expected[0], b"")

        self.assertSurvivesAllocationFailures(
            primed_encoder, lambda encoder: encoder.encode(4, [BIG_ENTRY]), expected
        )
