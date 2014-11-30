#!/usr/bin/python

import subprocess

DEBUG = False


def launch_command(command):
    """
    If the script is launched in debug mode, just prints the command.
    Otherwise, starts it with subprocess.call()
    """
    if DEBUG:
        print(" ".join(command))
    else:
        subprocess.call(command)


def qdisc_add(interface, algorithm, handle, parent=None,
              *args, **kwargs):
    """
    Add qdisc
    :param interface: target interface
    :param algorithm: algorithm used for this leaf (htb, pfifo, sfq, ...)
    :param handle: handle parameter for tc
    :param parent: if is None, the rule will be added as root. (default: None)

    **kwargs will be used for specific arguments, depending on the algorithm
    used.
    """
    command = ["tc", "qdisc", "add", "dev", interface]
    if parent is None:
        command.append("root")
    else:
        command += ["parent", parent]
    command += ["handle", str(handle)]
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)


def class_add(interface, parent, classid, algorithm="htb", **kwargs):
    """
    Add class
    :param interface: target interface
    :param parent: parent class/qdisc
    :param classid: id for the current class
    :param algorithm: algorithm used for this class (default: htb)

    **kwargs will be used for specific arguments, depending on the algorithm
    used.
    Parameters need to be in kbit. If the unit isn't indicated, add it
    automagically
    """
    command = ["tc", "class", "add", "dev", interface, "parent", parent,
               "classid", classid, algorithm]
    if algorithm == "htb":
        for key in ("rate", "ceil"):
            if key in kwargs.keys() and str(kwargs[key]).isnumeric():
                kwargs[key] = str(kwargs[key]) + "kbit"
        for key in ("burst", "cburst"):
            if key in kwargs.keys() and kwargs[key].isnumeric():
                kwargs[key] = kwargs[key] + "k"
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)
