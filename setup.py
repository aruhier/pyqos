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

setup(
    name="pyqos",
    version="0.2.1",

    description="Framework that helps setting a QoS on Linux",
    long_description=open(
        path.join(path.dirname(__file__), "README.mkd")
    ).read(),

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
    install_requires=["argparse", ],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', 'pytest-cov', "pytest-mock", "pytest-xdist"],
)
