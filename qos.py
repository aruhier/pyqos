#!/usr/bin/python
# Author: Anthony Ruhier
# Set QoS rules

import os
import subprocess
import argparse
import sys

try:
    from config import INTERFACES
except ImportError:
    print("No existing configuration. Please copy config.py.default as "
          "config.py and optionaly configure it for your setup.")
    exit(1)

import rules
import tools


def get_ifnames(interfaces_lst=INTERFACES):
    if_names = set()
    for interface in interfaces_lst.values():
        if "name" in interface.keys():
            if_names.add(interface["name"])
        else:
            if_names.update(get_ifnames(interfaces_lst=interface))
    return if_names


def apply_qos():
    # Clean old rules
    reset_qos()
    # Setting new rules
    print("Setting new rules")
    rules.apply_qos()


def reset_qos():
    print("Removing tc rules")
    ifnames = get_ifnames()
    tools.qdisc_del(ifnames, "htb", stderr=subprocess.DEVNULL)
    return


def show_qos():
    ifnames = get_ifnames()
    print("\n\t QDiscs details\n\t================\n")
    tools.qdisc_show(ifnames, "details")
    print("\n\t QDiscs stats\n\t==============\n")
    tools.qdisc_show(ifnames, "details")

if __name__ == '__main__':

    # Need to be root
    if os.geteuid() != 0:
        print("You need to be root to run this script. Relaunching with sudo...\n")
        subprocess.call(["sudo", sys.executable] + sys.argv)
        exit()

    # Set all arguments possible for this script
    parser = argparse.ArgumentParser(description="Script to set, show or delete QoS rules with TC")
    sp = parser.add_subparsers()
    sp_start = sp.add_parser("start", help="set QoS rules")
    sp_stop = sp.add_parser("stop", help="Remove all QoS rules")
    sp_show = sp.add_parser("show", help="Show QoS rules")

    # Set function to call for each options
    sp_start.set_defaults(func=apply_qos)
    sp_stop.set_defaults(func=reset_qos)
    sp_show.set_defaults(func=show_qos)

    # If no argument provided show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse argument and execute right function
    args = parser.parse_args()
    args.func()

