#!/usr/bin/python
# Author: Anthony Ruhier
# Set QoS rules

import os
import subprocess
import sys

try:
    from config import INTERFACES
except ImportError:
    print("No existing configuration. Please copy config.py.default as "
          "config.py and optionaly configure it for your setup.")
    exit(1)

import rules
import tools


def apply_qos():
    # Clean old rules
    reset_qos()
    # Setting new rules
    print("Setting new rules")
    rules.apply_qos()


def reset_qos():
    print("Removing tc rules")
    tools.qdisc_del(INTERFACES.values(), "htb", stderr=subprocess.DEVNULL)
    return


def show_qos():
    interfaces = INTERFACES.values()
    print("\n\t QDiscs details\n\t================\n")
    tools.qdisc_show(interfaces, "details")
    print("\n\t QDiscs stats\n\t==============\n")
    tools.qdisc_show(interfaces, "details")


def print_help():
    print("Script to set, show or delete QoS rules with TC\n")
    print("python3 qos.py [option]")
    print("[option]: ")
    print("\tstart: set QoS rules")
    print("\tstop: remove all QoS rules")
    print("\tshow: show QoS rules")
    exit()


# Need to be root
if os.geteuid() != 0:
    print("You need to be root to run this script. Relaunching with sudo...\n")
    subprocess.call(["sudo", ] + sys.argv)
    exit()

if len(sys.argv) != 2:
    print_help()
elif sys.argv[1] == "start":
    apply_qos()
elif sys.argv[1] == "stop":
    reset_qos()
elif sys.argv[1] == "show":
    show_qos()
else:
    print_help()
