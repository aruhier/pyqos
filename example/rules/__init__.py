#!/usr/bin/env python3

from pyqos import PyQOS
import config

app = PyQOS()
app.config.from_object(config)

from rules import upload, download
