pylsqpack
=========

.. image:: https://img.shields.io/pypi/l/pylsqpack.svg
   :target: https://pypi.python.org/pypi/pylsqpack
   :alt: License

.. image:: https://img.shields.io/pypi/v/pylsqpack.svg
   :target: https://pypi.python.org/pypi/pylsqpack
   :alt: Version

.. image:: https://img.shields.io/pypi/pyversions/pylsqpack.svg
   :target: https://pypi.python.org/pypi/pylsqpack
   :alt: Python versions

.. image:: https://github.com/aiortc/pylsqpack/workflows/tests/badge.svg
   :target: https://github.com/aiortc/pylsqpack/actions
   :alt: Tests

``pylsqpack`` is a wrapper around the `ls-qpack`_ library. It provides Python
`Decoder` and `Encoder` objects to read or write HTTP/3 headers compressed
with QPACK.

.. automodule:: pylsqpack

    .. autoclass:: Decoder
        :members:

    .. autoclass:: Encoder
        :members:


.. _ls-qpack: https://github.com/litespeedtech/ls-qpack/
