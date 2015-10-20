#!/usr/bin/python
# Author: Anthony Ruhier
# QoS for upload

from rules.qos_formulas import burst_formula, cburst_formula
from pyqos.algorithms.htb import HTBFilterPFIFO, HTBFilterSFQ


class Interactive(HTBFilterPFIFO):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    id = 100
    prio = 10
    mark = id
    rate = 3000
    ceil = (75,)
    burst = (burst_formula,)
    cburst = (cburst_formula,)


class TCP_ack(HTBFilterSFQ):
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast
    as possible when a host of the network is downloading. Uses htb then sfq.
    """
    id = 200
    prio = 20
    mark = id
    rate = (50, 100, 4000)
    ceil = (100, 2000)
    burst = (burst_formula,)
    cburst = (cburst_formula,)


class SSH(HTBFilterSFQ):
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !
    SFQ will mix the packets if there are several SSH connections in parallel
    and ensure that none has the priority
    """
    id = 300
    prio = 30
    mark = id
    rate = (20,)
    ceil = (100,)
    burst = (burst_formula,)
    cburst = (cburst_formula,)


class HTTP(HTBFilterSFQ):
    """
    Class for HTTP/HTTPS connections.
    """
    id = 400
    prio = 40
    mark = id
    rate = (20,)
    ceil = (100,)
    burst = (burst_formula,)
    cburst = (cburst_formula,)


class Default(HTBFilterSFQ):
    """
    Default class
    """
    id = 1000
    prio = 100
    mark = id
    rate = (60, 1000, 5000)
    ceil = (100,)
    burst = (burst_formula,)
    cburst = (cburst_formula,)
