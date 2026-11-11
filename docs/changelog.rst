Changelog
=========

.. currentmodule:: pylsqpack

1.1.0
-----

* Add a ``max_field_section_size`` argument to :class:`Decoder`, which limits
  the size of the decoded headers of a header block, counted as in
  :rfc:`9114#section-4.2.2`. It defaults to 256 KiB, so header blocks which
  decode to more than that are now refused. They raise
  :class:`FieldSectionTooLarge`, a subclass of :class:`DecompressionFailed`.
* Raise :class:`ValueError` for integer arguments which are out of range,
  instead of silently wrapping them around: settings must fit in 32 bits and
  stream IDs must be QUIC stream IDs.
* Raise :class:`TypeError` when arguments are passed to :class:`Encoder`,
  instead of ignoring them.
* Fix pending header blocks on 32-bit platforms: for stream IDs of 2**32 or
  more, they could not be resumed or cancelled.
* Show stream IDs in full in error messages.
* Document the exceptions, and the methods which raise them.

1.0.0
-----

* Adopt semantic versioning.
* Add :meth:`Decoder.cancel_stream` to cancel decoding for a reset or
  abandoned stream.
* Grow the encoder's buffers on demand instead of capping them at 4 kB, so
  that large header blocks (e.g. with large cookies) no longer fail to encode.
* Allocate the decoder's buffers using Python's memory allocator, making them
  visible to :mod:`tracemalloc`.
* Update vendored `ls-qpack`_ from version 2.6.2 to 2.7.0, which brings:

  * a fix for decoding header blocks when the encoder selects a dynamic table
    capacity lower than the maximum,
  * fixes for a use-after-free and a double-free,
  * stricter validation of encoder and decoder stream instructions, header
    lengths and Huffman padding.

.. _ls-qpack: https://github.com/litespeedtech/ls-qpack
