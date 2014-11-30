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
    print("Removing iptables rules...")
    subprocess.call(["iptables", "-t", "mangle", "-F"])
    subprocess.call(["iptables", "-t", "mangle", "-X"])
    print("Removing tc rules")
    for interface in (PUBLIC_IF, LAN_IF):
        subprocess.call(["tc", "qdisc", "del", "dev", interface, "root",
                         "handle", "1"])
    return


def show_qos():
    print("\n\t QDiscs details\n\t================\n")
    for interface in (PUBLIC_IF, LAN_IF):
        subprocess.call(["tc", "-d", "qdisc", "show", "dev", interface])
    print("\n\t QDiscs stats\n\t==============\n")
    for interface in (PUBLIC_IF, LAN_IF):
        subprocess.call(["tc", "-s", "qdisc", "show", "dev", interface])


def print_help():
    print("Script to set QoS rules\n")
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
