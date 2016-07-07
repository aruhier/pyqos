#!/usr/bin/env python3
# Author: Anthony Ruhier

"""
Framework that helps setting a QoS on Linux
See:
    https://github.com/Anthony25/python_tc_qos
"""

from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.mkd"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="pyqos",
    version="0.2.0",

    description="Framework that helps setting a QoS on Linux",
    long_description=long_description,

    url="https://github.com/Anthony25/pyqos",
    author="Anthony25 <Anthony Ruhier>",
    author_email="anthony.ruhier@gmail.com",

    license="Simplified BSD",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: BSD License",
    ],

    keywords="networking qos linux development",
    packages=["pyqos", ],
    install_requires=["argparse", ]
)
