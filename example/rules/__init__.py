#!/usr/bin/python

from pyqos import PyQOS
import config

app = PyQOS()
app.config.from_object(config)

from rules import upload, download
