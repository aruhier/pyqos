#!/usr/bin/python
# Author: Anthony Ruhier

import inspect

from pyqos import tools
from pyqos.backend import tc
from pyqos.exceptions import BadAttributeValueException, NoParentException
from . import EmptyObject, _BasicQDisc
from .classless_qdiscs import FQCodel, PFIFO, SFQ


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

    def _add_class(self):
        pass

    def add_child(self, class_child):
        """
        Add a class as children
        """
        class_child.parent = self
        self.children.append(class_child)

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.auto_quantum = auto_quantum
        self._add_class()
        for child in self.children:
            child.apply_qos(auto_quantum=auto_quantum)

    def __init__(self, classid=None, rate=None, ceil=None,
                 burst=None, cburst=None, quantum=None, prio=None,
                 children=None, *args, **kwargs):
        self._init_properties("rate", "ceil", "burst", "cburst")
        self.classid = classid if classid is not None else self.classid
        if rate is not None:
            self.rate = rate
        if ceil is not None:
            self.ceil = ceil
        if burst is not None:
            self.burst = burst
        if cburst is not None:
            self.cburst = cburst
        self._quantum = quantum
        self.prio = prio if prio is not None else self.prio
        self.children = children if children is not None else []


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

    def _add_class(self):
        """
        Add class to the interface
        """
        tc.qos_class_add(self.interface, parent=self.parent.classid,
                         classid=self.classid, rate=self.rate,
                         ceil=self.ceil, burst=self.burst, cburst=self.cburst,
                         prio=self.prio, quantum=self.quantum)


class RootHTBClass(HTBClass):
    """
    Root tc class, directly attached to the interface
    """
    #: interface
    _interface = None
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
        self.parent = qdisc_object
        self._root = qdisc_object
        self.classid = str(self.qdisc_prefix_id) + "1"
        super().__init__(*args, **kwargs)

    @property
    def root(self):
        """
        Return the qdisc class id
        """
        return self._root

    @property
    def interface(self):
        """
        Return the interface name
        """
        return self._interface

    def _add_qdisc(self):
        """
        Add the root qdisc
        """
        tc.qdisc_add(self.interface, self.qdisc_prefix_id, self.algorithm,
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
        self._add_qdisc()
        return super().apply_qos(
            auto_quantum=(auto_quantum and self.r2q is None)
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
        self.mark = mark if mark is not None else self.mark
        qdisc = qdisc if qdisc is not None else self.qdisc
        self.qdisc_kwargs = (qdisc_kwargs if qdisc_kwargs is not None
                             else self.qdisc_kwargs)
        if inspect.isclass(qdisc):
            self.qdisc = qdisc(parent=self, **self.qdisc_kwargs)
        else:
            self.qdisc = qdisc
            self.qdisc.parent = self
            for attr, value in self.qdisc_kwargs.items():
                setattr(qdisc, attr, value)
        super().__init__(*args, **kwargs)

    def _add_filter(self):
        """
        Add filter to the class
        """
        tc.filter_add(self.interface, parent=self.root.classid,
                      prio=self.prio, handle=self.mark, flowid=self.classid)

    def apply_qos(self, auto_quantum=True):
        """
        Apply qos with current attributes

        The function is recursive, so it will apply the qos of all children
        too.
        """
        self.auto_quantum = auto_quantum
        self._add_class()
        self.qdisc.apply()
        self._add_filter()
        for child in self.children:
            child.apply_qos(auto_quantum=auto_quantum)


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
