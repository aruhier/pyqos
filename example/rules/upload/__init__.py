#!/usr/bin/python

from rules import app
from pyqos.algorithms.htb import RootHTBClass
from .upload import Interactive, TCPACK, SSH, HTTP, Default

public_if = app.config["INTERFACES"]["public_if"]
root_class = RootHTBClass(
    interface=public_if["name"],
    rate=public_if["speed"],
    burst=public_if["speed"]/8,
    default=1500
)
root_class.add_child(Interactive())
root_class.add_child(TCPACK())
root_class.add_child(SSH())
root_class.add_child(HTTP())
root_class.add_child(Default())

app.run_list.append(root_class)
