#!/usr/bin/env python3
# Author: Anthony Ruhier

import logging

_logger = logging.getLogger("pyqos")


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


class _BasicQDisc():
    """
    Abstract class for QDisc
    """
    #: id
    _id = None
    #: interface
    _interface = None
    #: parent object
    parent = None
    #: QDisc ID
    id = None
    #: Interface linked to this qdisc
    interface = None

    def _getter_attr_shared_with_parents(self, attr):
        """
        Common getter for attr shared with the parent

        If any parent is linked to this qdisc, return its attribute value, or
        the local value otherwise.
        To use the value set directly on this qdisc attribute (and its
        parent one), set the parent attribute to None.
        """
        return (getattr(self, "_" + attr)
                if self.parent is None else getattr(self.parent, attr))

    def _setter_attr_shared_with_parents(self, attr, value):
        """
        Common setter for attr shared with the parent

        Usefull only when the QDisc is directly attached to an interface (= has
        no parent). Print a warning if this function is called when a parent is
        linked (because the value set will never be used).
        """
        if self.parent is not None:
            _logger.warning(
                "Setting \"" + attr + "\" is useless in this case because the "
                "QDisc has a parent, so it will not be used."
            )
        setattr(self, "_" + attr, value)

    def _get_id(self, obj=None):
        """
        Getter for id
        """
        if obj is not None:
            self = obj
        return self._getter_attr_shared_with_parents("id")

    def _set_id(self, obj=None, value=None):
        if obj is not None:
            self = obj
        return self._setter_attr_shared_with_parents("id", value)

    def _get_interface(self, obj=None):
        """
        Getter for the interface
        """
        return self._getter_attr_shared_with_parents("interface")

    def _set_interface(self, obj=None, value=None):
        return self._setter_attr_shared_with_parents("interface", value)

    def _init_properties(self, *args):
        """
        Little hack to allow overriding the class and conserving the properties
        without the need of overriding __init__
        """
        def set_property(attribute):
            cls = type(self)
            if not hasattr(cls, "__perinstance"):
                cls = type(cls.__name__, (cls,), {})
                cls.__perinstance = True
                self.__class__ = cls
            setattr(
                cls, attribute,
                property(
                    getattr(self, "_get_" + attribute),
                    getattr(self, "_set_" + attribute)
                )
            )

        for attribute in args:
            try:
                if not isinstance(getattr(type(self), attribute), property):
                    tmp = getattr(self, attribute)
                    set_property(attribute)
                    setattr(self, attribute, tmp)
            except AttributeError:
                set_property(attribute)

    def __init__(self, id=None, parent=None, interface=None, *args,
                 **kwargs):
        self._init_properties("id", "interface")
        if parent is not None:
            self.parent = parent
        if interface is not None:
            self.interface = interface
        if id is not None:
            self.id = id

    def apply(self, dryrun=False):
        raise NotImplementedError()


from . import classless_qdiscs, htb
