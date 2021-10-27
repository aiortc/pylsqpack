import os.path
import sys

import setuptools

root_dir = os.path.abspath(os.path.dirname(__file__))

about = {}
about_file = os.path.join(root_dir, "src", "pylsqpack", "about.py")
with open(about_file, encoding="utf-8") as fp:
    exec(fp.read(), about)

readme_file = os.path.join(root_dir, "README.rst")
with open(readme_file, encoding="utf-8") as f:
    long_description = f.read()

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
    name=about["__title__"],
    version=about["__version__"],
    description=about["__summary__"],
    long_description=long_description,
    url=about["__uri__"],
    author=about["__author__"],
    author_email=about["__email__"],
    license=about["__license__"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
    ],
    package_dir={"": "src"},
    package_data={"pylsqpack": ["py.typed", "__init__.pyi"]},
    packages=["pylsqpack"],
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
