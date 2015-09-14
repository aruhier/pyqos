#!/usr/bin/python
# Author: Anthony Ruhier

import tools
from exceptions import BadAttributeValueException, NoParentException


class EmptyObject():
    """
    Object that does nothing, but "nothing" can be useful

    Base object to simulate, for example, something already handled by another
    tool in the system. Just set as attribute everything it receives in
    parameter during the construction.
    """
    def __init__(self, **kwargs):
        """
        Set as attribute everything received
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class EmptyHTBClass():
    """
    HTB that does nothing but can be used as parent for example

    Can be useful to simulate, for example, a class already handled by another
    tool in the system.
    """
    #: parent object
    _parent = None
    #: root class: class directly attached to the interface
    _root = None
    #: interface
    _interface = None
    #: class id
    classid = None
    #: store the rate as it was defined during the init
    _rate = None
    #: store the ceil as it was defined during the init
    _ceil = None
    #: store the burst as it was defined during the init
    _burst = None
    #: store the cburst as it was defined during the init
    _cburst = None
    #: quantum (optional)
    quantum = None
    #: priority
    prio = None
    #: children class which will be attached to this class
    children = None

    def _compute_speeds(self, attr):
        """
        Compute the attribute value if it's relative

        :param attr: attribute associated to the speed to compute
        :type attr: tuple of 2 or 3 items: (percentage of the parent value,
                    min, [max])
        :return computed_speed: integer corresponding to the computed speed
        """
        if self._parent is None:
            raise NoParentException(
                str(attr) + " is relative and asked to be computed, but class "
                " has no parent."
            )
        parent_speed = getattr(self._parent, attr)
        if attr is "ceil" and parent_speed is None:
            parent_speed = getattr(self._parent, "rate")
        relative_rate = getattr(self, "_" + attr)
        if relative_rate == 3:
            coeff, speed_min, speed_max = relative_rate
        elif len(attr) == 2:
            coeff, speed_min = relative_rate
            speed_max = parent_speed
        else:
            coeff, speed_min, speed_max = relative_rate[0], 0, parent_speed
        return int(
            min(max(parent_speed * coeff/100, speed_min), speed_max)
        )

    def _get_rate(self, obj=None):
        """
        Getter for rate

        If _rate is an integer, will be used directly. Can also be a
        tupple to set a relative rate, equals to a % of the parent class rate:
        (percentage, rate_min, rate_max). The root class cannot have a relative
        rate.
        """
        return (self._compute_speeds("rate") if type(self._rate) is tuple
                else self._rate)

    def _set_rate(self, obj=None, value=None):
        """
        Setter for rate

        If rate is an integer, will be used directly. Can also be a
        tupple to set a relative rate, equals to a % of the parent class rate:
        (percentage, rate_min, rate_max). The root class cannot have a relative
        rate.
        """
        self._rate = value

    def _get_ceil(self, obj=None):
        """
        Getter for ceil

        If _ceil is an integer, will be used directly. Can also be a
        tupple to set a relative ceil, equals to a % of the parent class ceil:
        (percentage, ceil_min, ceil_max). The root class cannot have a relative
        ceil.
        """
        return (self._compute_speeds("ceil") if type(self._ceil) is tuple
                else self._ceil)

    def _set_ceil(self, obj=None, value=None):
        """
        Setter for ceil

        If ceil is an integer, will be used directly. Can also be a
        tupple to set a relative ceil, equals to a % of the parent class ceil:
        (percentage, ceil_min, ceil_max). The root class cannot have a relative
        ceil.
        """
        self._ceil = value

    def _getter_burst_cburst(self, attr):
        """
        Common getter for burst or cburst

        They can be a callback or a fixed value: If attr is an integer, its
        value will be returned directly.  Otherwise, if it is a tuple or a
        function, it will be considered as a callback.
        An argument obj=self will always be sent to the callback.

        :param attr: attr to get (self._cburst or self._burst)
        :return: result of the callback if any, otherwise the direct value of
                 the attribute
        """
        if type(attr) is not tuple:
            try:
                return attr()
            except TypeError:
                return attr
        if len(attr) == 3:
            callback, args, kwargs = attr
            return callback(obj=self, *args, **kwargs)
        elif len(attr) == 2:
            callback, args = attr
            return callback(obj=self, *args)
        else:
            callback = attr[0]
            return callback(self)

    def _get_burst(self, obj=None):
        """
        Burst can be a callback or a fixed value

        If _burst is an integer, its value will be returned directly.
        Otherwise, if it is a tuple, it will be considered as a callback.
        """
        return self._getter_burst_cburst(self._burst)

    def _set_burst(self, obj=None, value=None):
        self._burst = value

    def _get_cburst(self, obj=None):
        """
        CBurst can be a callback or a fixed value

        If _burst is an integer, its value will be returned directly.
        Otherwise, if it is a tuple, it will be considered as a callback.
        """
        return self._getter_burst_cburst(self._cburst)

    def _set_cburst(self, obj=None, value=None):
        self._cburst = value

    def _init_properties(self):
        def set_property(attribute):
            setattr(
                self.__class__, attribute,
                property(
                    getattr(self, "_get_" + attribute),
                    getattr(self, "_set_" + attribute)
                )
            )

        for attribute in ("rate", "ceil", "burst", "cburst"):
            try:
                if not isinstance(getattr(type(self), attribute), property):
                    tmp = getattr(self, attribute)
                    set_property(attribute)
                    setattr(self, attribute, tmp)
            except AttributeError:
                set_property(attribute)

    def _add_class(self):
        pass

    def _check_quantum(self):
        """
        Check if the quantum is not too high

        Kernel warnings that quantum is too high if it's superior to 18 000
        """
        pass

    def add_child(self, class_child):
        """
        Add a class as children
        """
        class_child.set_parent_root(parent=self)
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

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.compute(auto_quantum=auto_quantum)
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

    def compute(self, auto_quantum=True):
        """
        Compute values that can/need to be

        Compute class rate and ceil (compute when they are relatives, otherwise
        just copies the value defined). Computes the quantum.
        """
        if auto_quantum:
            self._check_quantum()

    def __init__(self, classid=None, rate=None, ceil=None,
                 burst=None, cburst=None, quantum=None, prio=None,
                 children=None, *args, **kwargs):
        self._init_properties()
        self.classid = classid if classid is not None else self.classid
        if rate is not None:
            self.rate = rate
        if ceil is not None:
            self.ceil = ceil
        if burst is not None:
            self.burst = burst
        if cburst is not None:
            self.cburst = cburst
        self.quantum = quantum if quantum is not None else self.quantum
        self.prio = prio if prio is not None else self.prio
        self.children = children if children is not None else []


class BasicHTBClass(EmptyHTBClass):
    """
    Basic class
    """
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

    def _add_class(self):
        """
        Add class to the interface
        """
        tools.class_add(self._interface, parent=self._parent.classid,
                        classid=self.classid, rate=self.rate,
                        ceil=self.ceil, burst=self.burst, cburst=self.cburst,
                        prio=self.prio, quantum=self.quantum)


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
        qdisc_object = EmptyObject(classid=str(self.qdisc_prefix_id) + "0")
        self._parent = qdisc_object
        self._root = qdisc_object
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
        if type(self.rate) is tuple:
            raise BadAttributeValueException(
                "Rate cannot be relative for a root class"
            )
        self.compute()
        self._add_qdisc()
        return super().apply_qos(
            auto_quantum=(auto_quantum and self.r2q is None)
        )


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
        tools.filter_add(self._interface, parent=self._root.classid,
                         prio=self.prio, handle=self.mark, flowid=self.classid)

    def _add_qdisc(self):
        raise NotImplemented

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.compute(auto_quantum=auto_quantum)
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
