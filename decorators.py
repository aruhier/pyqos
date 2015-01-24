#!/usr/bin/python
# Author: Anthony Ruhier
# Declares decorators


def multiple_interfaces(f):
    """
    Handle multiple interfaces for tc

    If the parameter "interface" is a list of multiple interfaces, it will
    execute the function f for each interface
    """
    def repeat_for_each_interface(interface, *args, **kwargs):
        if type(interface) is not str:
            for i in interface:
                repeat_for_each_interface(i, *args, **kwargs)
        else:
            f(interface, *args, **kwargs)
    return repeat_for_each_interface
