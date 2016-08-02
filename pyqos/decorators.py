#!/usr/bin/env python3
# Author: Anthony Ruhier
# Declares decorators

from functools import wraps


def multiple_interfaces(f):
    """
    Handle multiple interfaces for tc

    If the parameter "interface" is a list of multiple interfaces, it will
    execute the function f for each interface
    """
    @wraps(f)
    def repeat_for_each_interface(interface=None, *args, **kwargs):
        if type(interface) is not str and interface is not None:
            for i in interface:
                repeat_for_each_interface(i, *args, **kwargs)
        else:
            # keep interface as optional attribute for some functions
            if interface is None:
                f(*args, **kwargs)
            else:
                f(interface, *args, **kwargs)
    return repeat_for_each_interface
