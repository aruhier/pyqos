#!/usr/bin/python

from rules import app
from pyqos.algorithms.htb import RootHTBClass
from .download import Interactive, TCP_ack, SSH, HTTP, Default


lan_if = app.config["INTERFACES"]["lan_if"]
root_class = RootHTBClass(
    interface=lan_if["name"],
    rate=lan_if["speed"],
    burst=lan_if["speed"]/8,
    default=1500
)
root_class.add_child(Interactive())
root_class.add_child(TCP_ack())
root_class.add_child(SSH())
root_class.add_child(HTTP())
root_class.add_child(Default())

app.run_list.append(root_class)
