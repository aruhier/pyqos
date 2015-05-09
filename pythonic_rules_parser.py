#!/usr/bin/python
# Author: Thomas Gagneret
# Set QoS rules

try:
    from config import INTERFACES
except ImportError:
    print("No existing configuration. Please copy config.py.default as "
          "config.py and optionaly configure it for your setup.")
    exit(1)

import rules


def get_ifnames(interfaces_lst=INTERFACES):
    if_names = set()
    for interface in interfaces_lst.values():
        if "name" in interface.keys():
            if_names.add(interface["name"])
        else:
            if_names.update(get_ifnames(interfaces_lst=interface))
    return if_names


def setup_qos():
    rules.apply_qos()
