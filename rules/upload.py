#!/usr/bin/python
# QoS for upload

import tools
from config import PUBLIC_IF, UPLOAD


def interactive_class():
    """
    Interactive Class, for Low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    parent = "1:1"
    classid = "1:100"
    prio = 1
    mark = 100
    rate = UPLOAD * 10/100
    ceil = UPLOAD * 75/100
    minimum_ping = 10/1000
    expected_ping = 20/1000

    tools.class_add(PUBLIC_IF, parent, classid, rate=rate, ceil=ceil,
                    burst=expected_ping * rate,
                    cburst=minimum_ping * ceil, prio=prio)
    tools.qdisc_add(PUBLIC_IF, parent=classid, handle="1100:",
                    algorithm="pfifo")
    tools.filter_add(PUBLIC_IF, parent="1:0", prio=prio, handle=mark,
                     flowid="1:100")


def apply_qos():
    """
    Apply the QoS for the OUTPUT
    """
    # Creating the HTB root qdisc
    tools.qdisc_add(PUBLIC_IF, "1:", "htb", default=999)
    # Creating the main branch (htb)
    tools.class_add(PUBLIC_IF, parent="1:0", classid="1:1", rate=UPLOAD,
                    ceil=UPLOAD)
