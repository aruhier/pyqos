#!/usr/bin/python
# Author: Anthony Ruhier
# QoS for upload

import tools
from config import INTERFACES, UPLOAD

PUBLIC_IF = INTERFACES["PUBLIC_IF"]


def interactive_class():
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    parent = "1:1"
    classid = "1:100"
    prio = 10
    mark = 100
    rate = UPLOAD * 10/100
    ceil = UPLOAD * 75/100
    burst = 0.3 * ceil/8   # ceil in bytes during 0.3 seconds

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="1100:",
                    algorithm="pfifo")
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def tcp_ack_class():
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast
    as possible when a host of the network is downloading. Uses htb then sfq.
    """
    parent = "1:1"
    classid = "1:200"
    prio = 20
    mark = 200
    rate = UPLOAD * 50/100
    ceil = UPLOAD
    burst = 0.3 * ceil/8  # ceil in bytes during 0.3 seconds

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="1200:",
                    algorithm="sfq", perturb=10)
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def ssh_class():
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !
    SFQ will mix the packets if there are several SSH connections in parallel
    and ensure that none has the priority
    """
    parent = "1:1"
    classid = "1:300"
    prio = 30
    mark = 300
    rate = UPLOAD * 10/100
    ceil = UPLOAD
    burst = ceil/8  # ceil in bytes during 1 second

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="1300:",
                    algorithm="sfq", perturb=10)
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def http_class():
    """
    Class for HTTP/HTTPS connections.
    """
    parent = "1:1"
    classid = "1:400"
    prio = 40
    mark = 400
    rate = UPLOAD * 20/100
    ceil = UPLOAD
    burst = ceil/8  # ceil in bytes during 1 second

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=burst, prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="1400:",
                    algorithm="sfq", perturb=10)
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def default_class():
    """
    Default class
    """
    parent = "1:1"
    classid = "1:1000"
    prio = 100
    mark = 1000
    rate = UPLOAD * 60/100
    ceil = UPLOAD

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="11000:",
                    algorithm="sfq", perturb=10)
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid=classid)


def apply_qos():
    """
    Apply the QoS for the OUTPUT
    """
    # Creating the HTB root qdisc
    tools.qdisc_add(PUBLIC_IF, "1:", "htb", default=1000)
    # Creating the main branch (htb)
    tools.class_add(PUBLIC_IF, parent="1:0", classid="1:1", rate=UPLOAD,
                    ceil=UPLOAD)

    interactive_class()
    tcp_ack_class()
    ssh_class()
    http_class()
    default_class()
