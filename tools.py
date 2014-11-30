#!/usr/bin/python

import subprocess
from config import DEBUG


def launch_command(command):
    """
    If the script is launched in debug mode, just prints the command.
    Otherwise, starts it with subprocess.call()
    """
    if DEBUG:
        print(" ".join(command))
    else:
        subprocess.call(command)


def tc_qdisc(action, interface, algorithm, handle=None, parent=None, *args,
             **kwargs):
    """
    Add/change/replace/replace qdisc

    **kwargs will be used for specific arguments, depending on the algorithm
    used.

    :param action: "add", "replace", "change" or "delete"
    :param interface: target interface
    :param algorithm: algorithm used for this leaf (htb, pfifo, sfq, ...)
    :param handle: handle parameter for tc (default: None)
    :param parent: if is None, the rule will be added as root. (default: None)
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
    launch_command(command)


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
    return tc_qdisc("add", interface, algorithm, handle, parent, *args,
                    **kwargs)


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
    return tc_qdisc("delete", interface, algorithm, handle, parent, *args,
                    **kwargs)


def qdisc_show(show_format=None, interface=None):
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


def tc_class(action, interface, parent, classid=None, algorithm="htb",
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
            if key in kwargs.keys() and str(kwargs[key]).isnumeric():
                kwargs[key] = str(kwargs[key]) + "kbit"
        for key in ("burst", "cburst"):
            if key in kwargs.keys() and kwargs[key].isnumeric():
                kwargs[key] = kwargs[key] + "k"
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)


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
    return tc_class("add", interface, parent, classid, algorithm, **kwargs)


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
    return tc_class("delete", interface, parent, classid, algorithm, **kwargs)


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


def tc_filter(action, interface, prio, handle, flowid, parent=None,
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
    :param protocol: protocol to filter (default: ip)
    """
    command = ["tc", "filter", action, "dev", interface]
    if parent is not None:
        command += ["parent", parent]
    command += ["protocol", protocol, "prio", str(prio), "handle", str(handle),
                "fw", "flowid", flowid]
    for i, j in kwargs.items():
        command += [str(i), str(j)]
    launch_command(command)


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
    return tc_filter("add", interface, prio, handle, flowid, parent, protocol,
                     **kwargs)


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
    return tc_filter("delete", interface, prio, handle, flowid, parent,
                     protocol, **kwargs)


def filter_show(interface):
    """
    Show filters

    :param interface: target interface
    """
    launch_command(["tc", "filter", "show", "dev", interface])
