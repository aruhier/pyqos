#!/usr/bin/env python3
# Author: Anthony Ruhier

from pyqos import tools
from pyqos.backend import tc
from . import _BasicQDisc


class FQCodel(_BasicQDisc):
    """
    FQCodel (fq_codel) qdisc
    """
    #: when this limit is reached, incoming packets are dropped
    limit = None
    #: is the number of flows into which the incoming packets are classified
    flows = None
    #: is the acceptable minimum standing/persistent queue delay
    target = None
    #: is used to ensure that the measured minimum delay does not become too
    #: stale
    interval = None
    #: is the number of bytes used as 'deficit' in the fair queuing algorithm
    codel_quantum = None

    def __init__(self, limit=None, flows=None, target=None, interval=None,
                 codel_quantum=None, *args, **kwargs):
        self.limit = limit
        self.flows = flows
        self.target = target
        self.interval = interval
        self.codel_quantum = codel_quantum
        super().__init__(*args, **kwargs)

    def apply(self, dryrun=False):
        if self.codel_quantum is None:
            self.codel_quantum = tools.get_mtu(self.interface)
        tc.qdisc_add(
            self.interface,
            parent=self.parent.classid if self.parent else None,
            handle=self.id, algorithm="fq_codel",
            limit=self.limit, flows=self.flows, target=self.target,
            interval=self.interval, quantum=self.codel_quantum, dryrun=dryrun
        )


class PFIFO(_BasicQDisc):
    """
    PFIFO QDisc
    """
    def apply(self, dryrun=False):
        tc.qdisc_add(
            self.interface,
            parent=self.parent.classid if self.parent else None,
            handle=self.id, algorithm="pfifo", dryrun=dryrun
        )


class SFQ(_BasicQDisc):
    """
    SFQ QDisc
    """
    #: perturb parameter for sfq
    perturb = None

    def __init__(self, perturb=10, *args, **kwargs):
        self.perturb = perturb
        super().__init__(*args, **kwargs)

    def apply(self, dryrun=False):
        tc.qdisc_add(
            self.interface,
            parent=self.parent.classid if self.parent else None,
            handle=self.id, algorithm="sfq", perturb=self.perturb,
            dryrun=dryrun
        )
