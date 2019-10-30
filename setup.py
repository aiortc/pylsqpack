import os.path
import sys

import setuptools

root_dir = os.path.abspath(os.path.dirname(__file__))
readme_file = os.path.join(root_dir, "README.rst")
with open(readme_file, encoding="utf-8") as f:
    long_description = f.read()

include_dirs = [
    os.path.join("vendor", "ls-qpack"),
    os.path.join("vendor", "ls-qpack", "deps", "xxhash"),
]
if sys.platform == "win32":
    include_dirs.append(os.path.join("vendor", "ls-qpack", "wincompat"))

setuptools.setup(
    name="pylsqpack",
    version="0.3.3",
    description="Python wrapper for the ls-qpack QPACK library",
    long_description=long_description,
    url="https://github.com/aiortc/pylsqpack",
    author="Jeremy Lainé",
    author_email="jeremy.laine@m4x.org",
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
    ],
    package_dir={"": "src"},
    package_data={"pylsqpack": ["py.typed", "__init__.pyi"]},
    packages=["pylsqpack"],
    ext_modules=[
        setuptools.Extension(
            "pylsqpack._binding",
            include_dirs=include_dirs,
            sources=[
                "src/pylsqpack/binding.c",
                "vendor/ls-qpack/lsqpack.c",
                "vendor/ls-qpack/deps/xxhash/xxhash.c",
            ],
        ),
    ],
)
