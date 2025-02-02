import os.path
import sys

import setuptools
from wheel.bdist_wheel import bdist_wheel

extra_compile_args = []
include_dirs = [
    os.path.join("vendor", "ls-qpack"),
    os.path.join("vendor", "ls-qpack", "deps", "xxhash"),
]
if sys.platform == "win32":
    include_dirs.append(os.path.join("vendor", "ls-qpack", "wincompat"))
else:
    extra_compile_args = ["-std=c99"]


class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return "cp39", "abi3", plat

        return python, abi, plat


setuptools.setup(
    ext_modules=[
        setuptools.Extension(
            "pylsqpack._binding",
            define_macros=[("Py_LIMITED_API", "0x03080000")],
            extra_compile_args=extra_compile_args,
            include_dirs=include_dirs,
            py_limited_api=True,
            sources=[
                "src/pylsqpack/binding.c",
                "vendor/ls-qpack/lsqpack.c",
                "vendor/ls-qpack/deps/xxhash/xxhash.c",
            ],
        ),
    ],
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
