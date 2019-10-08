pylsqpack
=========

|pypi-v| |pypi-pyversions| |pypi-l| |travis|

.. |pypi-v| image:: https://img.shields.io/pypi/v/pylsqpack.svg
    :target: https://pypi.python.org/pypi/pylsqpack

.. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/pylsqpack.svg
    :target: https://pypi.python.org/pypi/pylsqpack

.. |pypi-l| image:: https://img.shields.io/pypi/l/pylsqpack.svg
    :target: https://pypi.python.org/pypi/pylsqpack

.. |travis| image:: https://img.shields.io/travis/com/aiortc/pylsqpack.svg
    :target: https://travis-ci.com/aiortc/pylsqpack

``pylsqpack`` is a wrapper around the `ls-qpack`_ library. It provides Python
`Decoder` and `Encoder` objects to read or write HTTP/3 headers compressed
with QPACK.

.. automodule:: pylsqpack

    .. autoclass:: Decoder
        :members:

    .. autoclass:: Encoder
        :members:


.. _ls-qpack: https://github.com/litespeedtech/ls-qpack/
