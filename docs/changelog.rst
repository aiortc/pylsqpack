Changelog
=========

.. currentmodule:: pylsqpack

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
