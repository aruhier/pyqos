#!/usr/bin/python
# Author: Anthony Ruhier

import tools


class BasicHTBClass():
    """
    Basic class
    """
    #: parent class
    _parent = None
    #: root class: class directly attached to the interface
    _root = None
    #: interface
    _interface = None
    #: class id
    classid = None
    #: rate
    rate = None
    #: ceil
    ceil = None
    #: burst
    burst = None
    #: cburst
    cburst = None
    #: quantum (optional)
    quantum = None
    #: priority
    prio = None
    #: children class which will be attached to this class
    children = None

    def __init__(self, classid=None, rate=None, ceil=None,
                 burst=None, cburst=None, quantum=None, prio=None,
                 children=None, *args, **kwargs):
        self.classid = classid if classid is not None else self.classid
        self.rate = rate if rate is not None else self.rate
        self.ceil = ceil if ceil is not None else self.ceil
        self.burst = burst if burst is not None else self.burst
        self.cburst = cburst if cburst is not None else self.cburst
        self.quantum = quantum if quantum is not None else self.quantum
        self.prio = prio if prio is not None else self.prio
        self.children = children if children is not None else []

    def _check_quantum(self):
        """
        Check if the quantum is not too high

        Kernel warnings that quantum is too high if it's superior to 18 000
        """
        if self.rate is None or self._interface is None:
            return

        # Adding 14 to the MTU to handle the ethernet overhead
        mtu = tools.get_mtu(self._interface) + 14
        self.quantum = mtu if self.quantum is None else self.quantum

    def add_child(self, class_child):
        """
        Add a class as children
        """
        class_child.set_parent_root(parent=self.classid)
        class_child.recursive_parent_change(self._root, self._interface)
        self.children.append(class_child)

    def recursive_parent_change(self, root=None, interface=None):
        """
        When rattaching a class to another class, have to change recursively
        the interface and root id of all children

        :param root: root id
        :param interface: interface of the parent
        """
        if root is not None:
            self._root = root
        if interface is not None:
            self._interface = interface
        for child in self.children:
            child.recursive_parent_change(root, interface)

    def _add_class(self):
        """
        Add class to the interface
        """
        tools.class_add(self._interface, parent=self._parent,
                        classid=self.classid, rate=self.rate,
                        ceil=self.ceil, burst=self.burst, cburst=self.cburst,
                        prio=self.prio, quantum=self.quantum)

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        if auto_quantum:
            self._check_quantum()
        self._add_class()
        for child in self.children:
            child.apply_qos(auto_quantum=auto_quantum)

    def set_parent_root(self, parent=None, root=None):
        """
        Set root and/or parent

        param parent: parent class id
        param root: root class id
        """
        if parent:
            self._parent = parent
        if root:
            self._root = root

    def set_interface(self, interface):
        """
        Set interface

        :param interface: interface to attach the class
        """
        self._interface = interface


class RootHTBClass(BasicHTBClass):
    """
    Root tc class, directly attached to the interface
    """
    #: main algorithm to use for the qdisc
    algorithm = None
    #: qdisc prefix
    qdisc_prefix_id = None
    #: default mark to catch
    default = None
    #: r2q, to influe on the quantum (optional)
    r2q = None

    def __init__(self, interface=None, algorithm="htb", qdisc_prefix_id="1:",
                 default=None, r2q=None, *args, **kwargs):
        self._interface = interface
        self.algorithm = algorithm
        self.qdisc_prefix_id = qdisc_prefix_id
        self.default = default
        self.r2q = r2q if r2q is not None else self.r2q
        self._parent = str(self.qdisc_prefix_id) + "0"
        self._root = self._parent
        self.classid = str(self.qdisc_prefix_id) + "1"
        super().__init__(*args, **kwargs)

    def _add_qdisc(self):
        """
        Add the root qdisc
        """
        tools.qdisc_add(self._interface, self.qdisc_prefix_id, self.algorithm,
                        default=self.default, r2q=self.r2q)

    def apply_qos(self, auto_quantum=True):
        """
        If the r2q has been defined, the quantum will not be defined
        automatiqually for children.
        """
        self._add_qdisc()
        return super().apply_qos(auto_quantum=(self.r2q is None))


class _BasicFilterHTBClass(BasicHTBClass):
    """
    Basic class with filtering
    """
    #: mark catch by the class
    mark = None

    def __init__(self, mark=None, *args, **kwargs):
        self.mark = mark if mark is not None else self.mark
        super().__init__(*args, **kwargs)

    def _add_filter(self):
        """
        Add filter to the class
        """
        tools.filter_add(self._interface, parent=self._root, prio=self.prio,
                         handle=self.mark, flowid=self.classid)

    def _add_qdisc(self):
        raise NotImplemented

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        if auto_quantum:
            self._check_quantum()
        self._add_class()
        self._add_qdisc()
        self._add_filter()
        for child in self.children:
            child.apply_qos(auto_quantum=auto_quantum)


class FQCodelClass(_BasicFilterHTBClass):
    """
    HTB class with a fq_codel qdisc builtin
    """
    #: when this limit is reached, incoming packets are dropped
    limit = None
    #: is the number of flows into which the incoming packets are classified
    flows = None
    #: is the acceptable minimum standing/persistent queue delay
    target = None
    #: is used to ensure that the measured minimum delay does not become too
    #  stale
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

    def _add_qdisc(self):
        if self.codel_quantum is None:
            self.codel_quantum = tools.get_mtu(self._interface)
        tools.qdisc_add(self._interface, parent=self.classid,
                        handle=tools.get_child_qdiscid(self.classid),
                        algorithm="fq_codel", limit=self.limit,
                        flows=self.flows, target=self.target,
                        interval=self.interval,
                        quantum=self.codel_quantum)


class SFQClass(_BasicFilterHTBClass):
    """
    HTB class with a SFQ qdisc builtin
    """
    #: perturb parameter for sfq
    perturb = None

    def __init__(self, perturb=10, *args, **kwargs):
        self.perturb = perturb
        super().__init__(*args, **kwargs)

    def _add_qdisc(self):
        tools.qdisc_add(self._interface, parent=self.classid,
                        handle=tools.get_child_qdiscid(self.classid),
                        algorithm="sfq", perturb=self.perturb)


class PFIFOClass(_BasicFilterHTBClass):
    """
    Basic filtering class with a PFIFO qdisc built in
    """
    def _add_qdisc(self):
        tools.qdisc_add(self._interface, parent=self.classid,
                        handle=tools.get_child_qdiscid(self.classid),
                        algorithm="pfifo")
