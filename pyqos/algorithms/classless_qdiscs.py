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


class Cake(_BasicQDisc):
    """
    Cake (cake) qdisc

    Complete documentation about this algorithm can be read here:
    https://www.bufferbloat.net/projects/codel/wiki/Cake/
    """

    def __init__(
            self, bandwidth=None, autorate_ingress=False, rtt_time=None,
            rtt_preset=None, priority_queue_preset=None, flow_isolation=None,
            nat=False, wash=False, split_gso=True, ack_filter=False,
            ack_filter_aggressive=False, memlimit=None, fwmark=None,
            atm_ptm_compensation=None, overhead=None, mpu=None,
            overhead_preset=None, ingress=False, *args, **kwargs
    ):
        #: bandwidth, in kbps.
        #: For now, does not allow a dynamic rate based on the parent one, as their
        #: is not a real purpose without allowing to handle priorities.
        self.bandwidth = bandwidth

        #: automatic compute of bandwidth. Can be used in conjunction of bandwidth
        #: to specify an initial estimate
        self.autorate_ingress = autorate_ingress

        #: rtt time, in ms
        self.rtt_time = rtt_time

        #: rtt preset. Useless if an rtt_time is given.
        self.rtt_preset = rtt_preset

        #: preset of priority queue
        self.priority_queue_preset = priority_queue_preset

        #: flow isolation technique
        self.flow_isolation = flow_isolation

        #: Enable or disable NAT lookup
        self.nat = nat

        #: Enable or disable extra diffserv "washing"
        self.wash = wash

        #: Enable or disable General Segmentation Offload (GSO) splitting
        self.split_gso = split_gso

        #: Enable or disable ACK filtering, changing the priority of TCP ACK
        self.ack_filter = ack_filter

        #: Enable aggressive mode for ACK filtering (useful only if ACK filter is
        #: enabled)
        self.ack_filter_aggressive = ack_filter_aggressive

        #: Memory limit, Bytes. If None, automatically computed by Cake.
        self.memlimit = memlimit

        #: Mask applied on the packet firewall mark. If indicated, only packets
        #: matching this mask will be accepted by the qdisc.
        self.fwmark = fwmark

        #: ATM or PTM compensation. Possible values: "atm", "ptm", "noatm". If
        # None, Cake set "noatm" by default.
        self.atm_ptm_compensation = atm_ptm_compensation

        #: Overhead to apply to the size of each packet, in Bytes. Range is -64 to
        #: 256
        self.overhead = overhead

        #: Rounds each packet (including overhead) up to a minimum length, in
        #: Bytes
        self.mpu = mpu

        #: Overhead preset to apply to the size of each packet. Useless if an
        #: overhead size if given. As some preset can be repeated, can be a list of
        #: string.
        self.overhead_preset = overhead_preset

        #: Is the qdisc ingress. If false, is egress
        self.ingress = ingress

        super().__init__(*args, **kwargs)

    def apply(self, dryrun=False):
        qdisc_args, qdisc_kwargs = self._build_tc_qdisc_opts()

        tc.qdisc_add(
            self.interface, handle=self.id, algorithm="cake",
            parent=self.parent.classid if self.parent else None,
            opts_args=qdisc_args, dryrun=dryrun, **qdisc_kwargs
        )

    def _build_tc_qdisc_opts(self):
        tc_args = []
        tc_kwargs = {
            "memlimit": self.memlimit, "fwmark": self.fwmark,
            "overhead": self.overhead, "mpu": self.mpu,
        }

        if self.bandwidth:
            tc_kwargs["bandwidth"] = "{}kbps".format(self.bandwidth)
        if self.autorate_ingress:
            tc_args.append("autorate-ingress")
        if self.rtt_time is not None:
            tc_kwargs["rtt"] = "{}ms".format(self.rtt_time)

        presets_args = (
            self.rtt_preset, self.priority_queue_preset, self.overhead_preset
        )
        for preset in presets_args:
            if isinstance(preset, (tuple, list)):
                tc_args.extend(preset)
            elif preset:
                tc_args.append(preset)
        if self.flow_isolation:
            tc_args.append(self.flow_isolation)

        tc_args.append("nat" if self.nat else "nonat")
        tc_args.append("wash" if self.wash else "nowash")
        tc_args.append("split-gso" if self.split_gso else "no-split-gso")

        if self.ack_filter:
            tc_args.append(
                "ack-filter-aggressive"
                if self.ack_filter_aggressive else "ack-filter"
            )
        else:
            tc_args.append("no-ack-filter")

        if self.atm_ptm_compensation:
            tc_args.append(self.atm_ptm_compensation)

        tc_args.append("ingress" if self.ingress else "egress")
        return tc_args, tc_kwargs
