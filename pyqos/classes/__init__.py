#!/usr/bin/python
# Author: Anthony Ruhier


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
