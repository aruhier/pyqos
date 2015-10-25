#!/usr/bin/env python3

from pyqos import PyQoS
import config

app = PyQoS()
app.config.from_object(config)

from rules import upload, download
