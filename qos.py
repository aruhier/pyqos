#!/usr/bin/python
# Set QoS rules

#############
# CONSTANTS #
#############

PUBLIC_IF = "eth0"  # network card to apply the QoS to
LAN_IF = "eth1"  # network card to apply the QoS to
UPLINK = 5000  # upload in kbits/s
DOWNLINK = 100000  # download in kbits/s

#################
# END_CONSTANTS #
#################

import os
import subprocess
import sys


def apply_qos():
    return


def reset_qos():
    return


def show_qos():
    return


def print_help():
    print("Script to set QoS rules\n")
    print("python3 qos.py [option]")
    print("[option]: ")
    print("    start: set QoS rules")
    print("    stop: remove all QoS rules")
    print("    show: show QoS rules")
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
