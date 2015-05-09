#!/usr/bin/python

from rules import upload, download


def apply_qos():
    upload.apply_qos()
    download.apply_qos()
