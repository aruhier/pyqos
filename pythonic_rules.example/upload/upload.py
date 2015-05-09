#!/usr/bin/python
# Author: Anthony Ruhier
# QoS for upload

from config import INTERFACES
from rules.qos_formulas import burst_formula, cburst_formula
from built_in_classes import PFIFOClass, SFQClass

UPLOAD = INTERFACES["public_if"]["speed"]


class Interactive(PFIFOClass):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    classid = "1:100"
    prio = 10
    mark = 100
    rate = UPLOAD * 10/100
    ceil = UPLOAD * 75/100
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class TCPACK(SFQClass):
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast
    as possible when a host of the network is downloading. Uses htb then sfq.
    """
    classid = "1:200"
    prio = 20
    mark = 200
    rate = UPLOAD * 50/100
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class SSH(SFQClass):
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !
    SFQ will mix the packets if there are several SSH connections in parallel
    and ensure that none has the priority
    """
    classid = "1:300"
    prio = 30
    mark = 300
    rate = UPLOAD * 10/100
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class HTTP(SFQClass):
    """
    Class for HTTP/HTTPS connections.
    """
    classid = "1:400"
    prio = 40
    mark = 400
    rate = UPLOAD * 20/100
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class Default(SFQClass):
    """
    Default class
    """
    classid = "1:1000"
    prio = 100
    mark = 1000
    rate = UPLOAD * 60/100
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
