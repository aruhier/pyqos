#!/usr/bin/python

from rules import app
from pyqos.algorithms.htb import RootHTBClass
from .upload import Interactive, TCP_ack, SSH, HTTP, Default

public_if = app.config["INTERFACES"]["public_if"]
root_class = RootHTBClass(
    interface=public_if["name"],
    rate=public_if["speed"],
    burst=public_if["speed"]/8,
    default=1500
)
root_class.add_child(Interactive(), TCP_ack(), SSH(), HTTP(), Default())
app.run_list.append(root_class)
