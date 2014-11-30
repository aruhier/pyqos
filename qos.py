#!/usr/bin/python
# Set QoS rules

#############
# CONSTANTS #
#############

PUBLIC_IF = "eth0"  # network card to apply the QoS to
LAN_IF = "eth1"  # network card to apply the QoS to
UPLINK = 5000  # upload in kbits/s
DOWNLINK = 100000  # download in kbits/s
DEBUG = False

#################
# END_CONSTANTS #
#################

import os
import subprocess
import sys

import tools
tools.DEBUG = DEBUG


def apply_qos():
    # Clean old rules
    reset_qos()
    return


def reset_qos():
    print("Removing iptables rules...")
    tools.launch_command(["iptables", "-t", "mangle", "-F"])
    tools.launch_command(["iptables", "-t", "mangle", "-X"])
    print("Removing tc rules")
    for interface in (PUBLIC_IF, LAN_IF):
        tools.qdisc_del(interface, "htb")
    return


def show_qos():
    print("\n\t QDiscs details\n\t================\n")
    for interface in (PUBLIC_IF, LAN_IF):
        tools.qdisc_show("details", interface)
    print("\n\t QDiscs stats\n\t==============\n")
    for interface in (PUBLIC_IF, LAN_IF):
        tools.qdisc_show("stats", interface)


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
