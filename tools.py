#!/usr/bin/python
# Author: Anthony Ruhier

import subprocess
from decorators import multiple_interfaces
from config import DEBUG


def launch_command(command, stderr=None):
    """
    If the script is launched in debug mode, just prints the command.
    Otherwise, starts it with subprocess.call()
    """
    if DEBUG:
        print(" ".join(command))
    else:
        r = subprocess.call(command, stderr=stderr)
        if r != 0:
            if stderr == subprocess.DEVNULL:
                return
            print("Error: ", file=stderr)
            print(" ".join(command), file=stderr)


@multiple_interfaces
def tc_qdisc(interface, action, algorithm, handle=None, parent=None,
             stderr=None, *args, **kwargs):
    """
    Add/change/replace/replace qdisc

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param action: "add", "replace", "change" or "delete"
    :param interface: target interface
    :param algorithm: algorithm used for this leaf (htb, pfifo, sfq, ...)
    :param handle: handle parameter for tc (default: None)
    :param parent: if is None, the rule will be added as root. (default: None)
    :param stderr: indicates stderr to use during the tc commands execution
    """
    command = ["tc", "qdisc", action, "dev", interface]
    if parent is None:
        command.append("root")
    else:
        command += ["parent", parent]
    if handle is not None:
        command += ["handle", str(handle)]
    command.append(algorithm)
    for i, j in kwargs.items():
        command += [str(i), str(j)]

    launch_command(command, stderr)


@multiple_interfaces
def qdisc_add(interface, handle, algorithm, parent=None, *args,
              **kwargs):
    """
    Add qdisc

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param interface: target interface
    :param algorithm: algorithm used for this leaf (htb, pfifo, sfq, ...)
    :param handle: handle parameter for tc
    :param parent: if is None, the rule will be added as root. (default: None)
    """
    return tc_qdisc(interface, "add", algorithm, handle, parent, *args,
                    **kwargs)


@multiple_interfaces
def qdisc_del(interface, algorithm, handle=None, parent=None, *args,
              **kwargs):
    """
    Delete qdisc

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param interface: target interface
    :param algorithm: algorithm used for this leaf (htb, pfifo, sfq, ...)
    :param handle: handle parameter for tc (default: None)
    :param parent: if is None, the rule will be added as root. (default: None)
    """
    return tc_qdisc(interface, "delete", algorithm, handle, parent, *args,
                    **kwargs)


@multiple_interfaces
def qdisc_show(interface=None, show_format=None):
    """
    Show qdiscs

    :param show_format: option "FORMAT" for tc. (default: None)
        "stats" -> -s
        "details" -> -d
        "raw" -> -r
        "pretty" -> -p
        "iec" -> -i
    :param interface: target interface (default: None)
    """
    formats = {"stats": "-s", "details": "-d", "raw": "-r", "pretty": "-p",
               "iec": "-i"}
    correct_format = formats.get(show_format, None)
    command = ["tc"]
    if show_format is not None:
        command.append(correct_format)
    command += ["qdisc", "show"]
    if interface is not None:
        command += ["dev", interface]
    launch_command(command)


def get_child_qdiscid(classid):
    """
    Return the id to handle for a child qdisc. By convention, it will take his
    parent class id

    :param classid: parent class id
    """
    return classid[classid.find(":") + 1:]


@multiple_interfaces
def tc_class(interface, action, parent, classid=None, algorithm="htb",
             **kwargs):
    """
    Add/change/replace/replace class

    **kwargs will be used for specific arguments, depending on the algorithm
    used.
    Parameters need to be in kbit. If the unit isn't indicated, add it
    automagically

    :param action: "add", "replace", "change" or "delete"
    :param interface: target interface
    :param parent: parent class/qdisc
    :param classid: id for the current class (default: None)
    :param algorithm: algorithm used for this class (default: htb)
    """
    command = ["tc", "class", action, "dev", interface, "parent", parent]
    if classid is not None:
        command += ["classid", classid]
    command.append(algorithm)
    if algorithm == "htb":
        for key in ("rate", "ceil"):
            if key in kwargs.keys():
                try:
                    kwargs[key] = str(int(kwargs[key])) + "kbit"
                except:
                    pass
        for key in ("burst", "cburst"):
            if key in kwargs.keys():
                try:
                    kwargs[key] = str(int(kwargs[key])) + "k"
                except:
                    pass
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)


@multiple_interfaces
def class_add(interface, parent, classid, algorithm="htb", **kwargs):
    """
    Add class

    **kwargs will be used for specific arguments, depending on the algorithm
    used.
    Parameters need to be in kbit. If the unit isn't indicated, add it
    automagically

    :param interface: target interface
    :param parent: parent class/qdisc
    :param classid: id for the current class (default: None)
    :param algorithm: algorithm used for this class (default: htb)
    """
    return tc_class(interface, "add", parent, classid, algorithm, **kwargs)


@multiple_interfaces
def class_del(interface, parent, classid=None, algorithm="htb", **kwargs):
    """
    Delete class

    **kwargs will be used for specific arguments, depending on the algorithm
    used.
    Parameters need to be in kbit. If the unit isn't indicated, add it
    automagically

    :param interface: target interface
    :param parent: parent class/qdisc
    :param classid: id for the current class (default: None)
    :param algorithm: algorithm used for this class (default: htb)
    """
    return tc_class(interface, "delete", parent, classid, algorithm, **kwargs)


@multiple_interfaces
def class_show(interface, show_format=None):
    """
    Show classes

    :param interface: target interface
    :param show_format: option "FORMAT" for tc. (default: None)
        "stats" -> -s
        "details" -> -d
        "raw" -> -r
        "pretty" -> -p
        "iec" -> -i
    """
    formats = {"stats": "-s", "details": "-d", "raw": "-r", "pretty": "-p",
               "iec": "-i"}
    correct_format = formats.get(show_format, None)
    command = ["tc"]
    if show_format is not None:
        command.append(correct_format)
    command += ["class", "show", "dev", interface]
    launch_command(command)


@multiple_interfaces
def tc_filter(interface, action, prio, handle, flowid, parent=None,
              protocol="ip", **kwargs):
    """
    Add/change/replace/delete filter

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param action: "add", "replace", "change" or "delete"
    :param interface: target interface
    :param prio: priority
    :param handle: filter id
    :param flowid: target class
    :param parent: parent class/qdisc (default: None)
    :param protocol: protocol to filter. Use ipv6 for IPv6 (default: ip)
    """
    command = ["tc", "filter", action, "dev", interface]
    if parent is not None:
        command += ["parent", parent]
    command += ["protocol", protocol, "prio", str(prio), "handle", str(handle),
                "fw", "flowid", flowid]
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)


@multiple_interfaces
def filter_add(interface, parent, prio, handle, flowid, protocol="ip",
               **kwargs):
    """
    Add filter

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param interface: target interface
    :param parent: parent class/qdisc
    :param prio: priority
    :param handle: filter id
    :param flowid: target class
    :param protocol: protocol to filter (default: ip)
    """
    return tc_filter(interface, "add", prio, handle, flowid, parent, protocol,
                     **kwargs)


@multiple_interfaces
def filter_del(interface, prio, handle, flowid, parent=None, protocol="ip",
               **kwargs):
    """
    Delete filter

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param interface: target interface
    :param prio: priority
    :param handle: filter id
    :param flowid: target class
    :param parent: parent class/qdisc (default: None)
    :param protocol: protocol to filter (default: ip)
    """
    return tc_filter(interface, "delete", prio, handle, flowid, parent,
                     protocol, **kwargs)


@multiple_interfaces
def filter_show(interface):
    """
    Show filters

    :param interface: target interface
    """
    launch_command(["tc", "filter", "show", "dev", interface])
