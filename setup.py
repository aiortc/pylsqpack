import os.path
import sys

import setuptools

extra_compile_args = []
include_dirs = [
    os.path.join("vendor", "ls-qpack"),
    os.path.join("vendor", "ls-qpack", "deps", "xxhash"),
]
if sys.platform == "win32":
    include_dirs.append(os.path.join("vendor", "ls-qpack", "wincompat"))
else:
    extra_compile_args = ["-std=c99"]

setuptools.setup(
    ext_modules=[
        setuptools.Extension(
            "pylsqpack._binding",
            extra_compile_args=extra_compile_args,
            include_dirs=include_dirs,
            sources=[
                "src/pylsqpack/binding.c",
                "vendor/ls-qpack/lsqpack.c",
                "vendor/ls-qpack/deps/xxhash/xxhash.c",
            ],
        ),
    ],
)
