#!/usr/bin/python
# Author: Anthony Ruhier
# Set QoS rules

import os
import subprocess
import argparse
import sys
import logging

try:
    from config import DEBUG
except ImportError:
    DEBUG = False

import tools


def run_as_root():
    """
    Restart the script as root
    """
    if os.geteuid() != 0:
        print("You need to be root to run this script. Relaunching with "
              "sudo...\n")
        subprocess.call(["sudo", sys.executable] + sys.argv)
        exit()


def apply_qos():
    run_as_root()
    # Clean old rules
    reset_qos()
    # Setting new rules
    print("Setting new rules")

    setup_qos()


def reset_qos():
    run_as_root()
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


def set_debug(level):
    if level or DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        stream=sys.stderr,
        format="[%(levelname)s] %(message)s (%(filename)s:%(lineno)d) ",
        level=log_level
    )

if __name__ == '__main__':
    # Set all arguments possible for this script
    parser = argparse.ArgumentParser(
        description="Script to set, show or delete QoS rules with TC"
    )

    # Start/Stop/Show command
    sp_action = parser.add_subparsers()
    sp_start = sp_action.add_parser("start", help="set QoS rules")
    sp_stop = sp_action.add_parser("stop", help="Remove all QoS rules")
    sp_show = sp_action.add_parser("show", help="Show QoS rules")

    # Set function to call for each options
    sp_start.set_defaults(func=apply_qos)
    sp_stop.set_defaults(func=reset_qos)
    sp_show.set_defaults(func=show_qos)

    # Debug option
    parser.add_argument('-d', '--debug', help="Set the debug level",
                        dest="debug", action="store_true")

    # Different ways to create QoS
    parser_group = parser.add_mutually_exclusive_group()

    # Use class rules
    parser_group.add_argument('-p', '--pythonic',
                              help="Use pythonic rules (default)",
                              dest="pythonic", action="store_true")
    # Use tree rules
    parser_group.add_argument('-t', '--tree', help="Use tree rules",
                              dest="tree", action="store_true")

    # If no argument provided show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse argument
    args = parser.parse_args()

    # Set debug mode
    set_debug(args.debug)

    if args.tree:
        from tree_rules_parser import setup_qos, get_ifnames
    else:
        from pythonic_rules_parser import setup_qos, get_ifnames

    # Execute correct function, or print usage
    try:
        args.func()
    except AttributeError:
        parser.print_usage()
        sys.exit(1)
