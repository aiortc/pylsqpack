import os
from glob import glob
from subprocess import check_call

import pkgconfig
import setuptools
from wheel.bdist_wheel import bdist_wheel

class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return "cp39", "abi3", plat

        return python, abi, plat

ext = setuptools.Extension(
    "pylsqpack._binding",
    define_macros=[("Py_LIMITED_API", "0x03080000")],
    py_limited_api=True,
    extra_compile_args=[],
    sources=["src/pylsqpack/binding.c"],
)

if not pkgconfig.installed("lsqpack", ">= 2.6.2"):
    check_call(["vcpkg", "install"])
    prefix = glob("vcpkg_installed/*-*")[0]
    os.environ["PKG_CONFIG"] = os.path.join(prefix, "tools/pkgconf/pkgconf")
    os.environ["PKG_CONFIG_PATH"] = os.path.join(prefix, "lib/pkgconfig")

pkgconfig.configure_extension(ext, "lsqpack", keep_system=("cflags", "libs"))

setuptools.setup(
    ext_modules=[ext],
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
