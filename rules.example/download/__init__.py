#!/usr/bin/python

from config import INTERFACES
from built_in_classes import RootHTBClass
from .download import Interactive, TCP_ack, SSH, HTTP, Default


def apply_qos():
    lan_if = INTERFACES["lan_if"]
    root_class = RootHTBClass(
        interface=lan_if["name"],
        rate=lan_if["speed"],
        burst=lan_if["speed"]/8,
        qdisc_prefix_id="1:",
        default=1500
    )
    root_class.add_child(Interactive())
    root_class.add_child(TCP_ack())
    root_class.add_child(SSH())
    root_class.add_child(HTTP())
    root_class.add_child(Default())

    root_class.apply_qos()
