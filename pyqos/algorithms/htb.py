#!/usr/bin/python
# Author: Anthony Ruhier

import inspect

from pyqos import tools
from pyqos.backend import tc
from pyqos.exceptions import BadAttributeValueException, NoParentException
from . import _BasicQDisc
from .classless_qdiscs import FQCodel, PFIFO, SFQ


class HTBQdisc(_BasicQDisc):
    """
    Implement the qdisc which will be directly set on the network interface
    """
    @property
    def id(self):
        return str(self.parent.branch_id) + ":"

    @property
    def classid(self):
        return self.id

    @property
    def default(self):
        return self.parent.default

    @property
    def r2q(self):
        return self.parent.r2q

    def apply(self, dryrun=False):
        tc.qdisc_add(self.interface, self.id, "htb",
                     default=self.default, r2q=self.r2q, dryrun=dryrun)


class EmptyHTBClass(_BasicQDisc):
    """
    HTB that does nothing but can be used as parent for example

    Can be useful to simulate, for example, a class already handled by another
    tool in the system.
    """
    #: store the rate as it was defined during the init
    _rate = None
    #: store the ceil as it was defined during the init
    _ceil = None
    #: store the burst as it was defined during the init
    _burst = None
    #: store the cburst as it was defined during the init
    _cburst = None
    #: parent object
    parent = None
    #: quantum (optional)
    _quantum = None
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
        if self.parent is None:
            raise NoParentException(
                str(attr) + " is relative and asked to be computed, but class "
                " has no parent."
            )
        parent_speed = getattr(self.parent, attr)
        if attr is "ceil" and parent_speed is None:
            parent_speed = getattr(self.parent, "rate")
        relative_speed = getattr(self, "_" + attr)
        if len(relative_speed) == 3:
            coeff, speed_min, speed_max = relative_speed
        elif len(relative_speed) == 2:
            coeff, speed_min = relative_speed
            speed_max = parent_speed
        else:
            coeff, speed_min, speed_max = relative_speed[0], 0, parent_speed
        return int(
            min(max(parent_speed * coeff/100, speed_min), speed_max)
        )

    @property
    def root(self):
        """
        Get the root of the current branch
        """
        if self.parent is None:
            raise NoParentException(
                "The class is not linked to a root class."
            )
        return self.parent.root

    @property
    def interface(self):
        """
        Get the interface of the current branch
        """
        if self.parent is None:
            raise NoParentException(
                "The class is not linked to a root class."
            )
        return self.parent.interface

    @property
    def quantum(self):
        """
        Quantum value
        """
        return self._quantum

    @property
    def branch_id(self):
        """
        Id of the current branch
        """
        return self.root.branch_id

    @property
    def classid(self):
        """
        Return the full_id, corresponding to "branch_id:id"
        """
        return str(self.branch_id) + ":" + str(self.id)

    def _get_rate(self, obj=None):
        """
        Getter for rate

        If _rate is an integer, will be used directly. Can also be a
        tupple to set a relative rate, equals to a % of the parent class rate:
        (percentage, rate_min, rate_max). The root class cannot have a relative
        rate.
        """
        if obj is not None:
            self = obj
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
        if obj is not None:
            self = obj
        self._rate = value

    def _get_ceil(self, obj=None):
        """
        Getter for ceil

        If _ceil is an integer, will be used directly. Can also be a
        tupple to set a relative ceil, equals to a % of the parent class ceil:
        (percentage, ceil_min, ceil_max). The root class cannot have a relative
        ceil.
        """
        if obj is not None:
            self = obj
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
        if obj is not None:
            self = obj
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
        if obj is not None:
            self = obj
        return self._getter_burst_cburst(self._burst)

    def _set_burst(self, obj=None, value=None):
        if obj is not None:
            self = obj
        self._burst = value

    def _get_cburst(self, obj=None):
        """
        CBurst can be a callback or a fixed value

        If _burst is an integer, its value will be returned directly.
        Otherwise, if it is a tuple, it will be considered as a callback.
        """
        if obj is not None:
            self = obj
        return self._getter_burst_cburst(self._cburst)

    def _set_cburst(self, obj=None, value=None):
        if obj is not None:
            self = obj
        self._cburst = value

    def _add_class(self):
        pass

    def add_child(self, class_child):
        """
        Add a class as children
        """
        class_child.parent = self
        self.children.append(class_child)

    def apply(self, auto_quantum=True, dryrun=False):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.auto_quantum = auto_quantum
        self._add_class(dryrun=dryrun)
        for child in self.children:
            child.apply(auto_quantum=auto_quantum, dryrun=dryrun)

    def __init__(self, id=None, rate=None, ceil=None,
                 burst=None, cburst=None, quantum=None, prio=None,
                 children=None, *args, **kwargs):
        self._init_properties("rate", "ceil", "burst", "cburst")
        self.id = id or self.id
        if rate is not None:
            self.rate = rate
        if ceil is not None:
            self.ceil = ceil
        if burst is not None:
            self.burst = burst
        if cburst is not None:
            self.cburst = cburst
        self._quantum = quantum
        self.prio = prio or self.prio
        self.children = children or []


class HTBClass(EmptyHTBClass):
    """
    Basic class
    """
    @property
    def quantum(self):
        """
        Quantum value
        """
        try:
            if self.auto_quantum and self._quantum is None:
                return tools.get_mtu(self.interface) + 14
        except AttributeError:
            return self._quantum

    def _add_class(self, dryrun=False):
        """
        Add class to the interface
        """
        tc.qos_class_add(self.interface, parent=self.parent.classid,
                         classid=self.classid, rate=self.rate,
                         ceil=self.ceil, burst=self.burst, cburst=self.cburst,
                         prio=self.prio, quantum=self.quantum, dryrun=dryrun)


class RootHTBClass(HTBClass):
    """
    Root tc class, directly attached to the interface
    """
    #: interface
    _interface = None
    id = 1
    #: branch id (and id of the root qdisc)
    branch_id = None
    #: default mark to catch
    default = None
    #: r2q, to influe on the quantum (optional)
    r2q = None

    @property
    def root(self):
        return self

    @property
    def interface(self):
        """
        Return the interface name
        """
        return self._interface

    def __init__(self, interface=None, branch_id=1,
                 default=None, r2q=None, *args, **kwargs):
        self._interface = interface
        self.default = default
        self.r2q = r2q or self.r2q
        self.branch_id = branch_id or self.branch_id
        self._qdisc = HTBQdisc(parent=self)
        # Needed with inherited functions
        self.parent = self._qdisc
        super().__init__(*args, **kwargs)

    def apply(self, auto_quantum=True, dryrun=False):
        """
        If the r2q has been defined, the quantum will not be defined
        automatiqually for children.
        """
        if type(self.rate) is tuple:
            raise BadAttributeValueException(
                "Rate cannot be relative for a root class"
            )
        self._qdisc.apply(dryrun=dryrun)
        return super().apply(
            auto_quantum=(auto_quantum and self.r2q is None), dryrun=dryrun
        )


class HTBFilter(HTBClass):
    """
    Basic class with filtering
    """
    #: mark catch by the class
    mark = None
    #: qdisc associated. Can be a class of an already initialized qdisc.
    qdisc = None
    #: dict used during the construction **ONLY**, used as a kwargs to set the
    #  qdisc attributes.
    qdisc_kwargs = dict()

    def __init__(self, mark=None, qdisc=None, qdisc_kwargs=None, *args,
                 **kwargs):
        self.mark = mark or self.mark
        qdisc = qdisc or self.qdisc
        self.qdisc_kwargs = qdisc_kwargs or self.qdisc_kwargs
        if inspect.isclass(qdisc):
            self.qdisc = qdisc(parent=self, **self.qdisc_kwargs)
        else:
            self.qdisc = qdisc
            self.qdisc.parent = self
            for attr, value in self.qdisc_kwargs.items():
                setattr(qdisc, attr, value)
        super().__init__(*args, **kwargs)

    def _add_filter(self, dryrun=False):
        """
        Add filter to the class
        """
        tc.filter_add(self.interface, parent=str(self.branch_id) + ":",
                      prio=self.prio, handle=self.mark, flowid=self.classid,
                      dryrun=dryrun)

    def apply(self, auto_quantum=True, dryrun=False):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.auto_quantum = auto_quantum
        self._add_class(dryrun=dryrun)
        self.qdisc.apply(dryrun=dryrun)
        self._add_filter(dryrun=dryrun)
        for child in self.children:
            child.apply(auto_quantum=auto_quantum, dryrun=dryrun)


class HTBFilterFQCodel(HTBFilter):
    """
    Lazy wrapper to get an HTB class with a filter and a FQCodel qdisc already
    set
    """
    qdisc = FQCodel


class HTBFilterPFIFO(HTBFilter):
    """
    Lazy wrapper to get an HTB class with a filter and a PFIFO qdisc already
    set
    """
    qdisc = PFIFO


class HTBFilterSFQ(HTBFilter):
    """
    Lazy wrapper to get an HTB class with a filter and a SFQ qdisc already set
    """
    qdisc = SFQ
