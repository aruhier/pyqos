#!/usr/bin/python
# Author: Anthony Ruhier

import logging

logging.basicConfig(
    format="[%(levelname)s] %(message)s (%(filename)s:%(lineno)d) "
)
_logger = logging.Logger("pyqos")

from pyqos.app import PyQOS
