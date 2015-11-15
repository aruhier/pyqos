#!/usr/bin/env python3
# Author: Anthony Ruhier

import errno
import importlib
import logging
import os
import types


class Config(dict):
    """
    Works like a dict but can be filled directly from a python configuration
    file. Inspired from the Flask Config class (a part of their code has been
    copied here).

    Only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.

    :param root_path: path to which files are read relative from.  When the
                      config object is created by the application, this is
                      the application's :attr:`~pyqos.PyQoS.root_path`.
    :param defaults: an optional dictionary of default values
    """
    def __init__(self, root_path, defaults=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path or "./"
        self.refresh_global_logger_lvl()

    def refresh_global_logger_lvl(self):
        if self["DEBUG"] or self["DRYRUN"]:
            logging.getLogger("pyqos").setLevel(logging.DEBUG)

    def from_pyfile(self, filename, silent=False):
        """
        Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.

        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        """
        filename = os.path.join(self.root_path, filename)
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """
        Updates the values from the given object.  An object can be of one
        of the following two types:

        - a string: in this case the object with that name will be imported
        - an actual object reference: that object is used directly

        Objects are usually either modules or classes.
        Just the uppercase variables in that object are stored in the config.
        Example usage::

            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)

        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        :param obj: an import name or object
        """
        if isinstance(obj, str):
            obj = importlib.import_module(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)


class ConfigAttribute(object):
    """
    Makes an attribute forward to the config

    Again, copied from the Flask project
    """
    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        # When setting the log level, change the global logger level
        obj.config[self.__name__] = value
        obj.config.refresh_global_logger_lvl()
