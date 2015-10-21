#!/usr/bin/python
# Author: Anthony Ruhier

import argparse
import logging
import os
import subprocess
import sys

from pyqos import _logger
from pyqos.backend import tc
from pyqos.config import Config, ConfigAttribute


class PyQOS():
    """
    Application to simplify the initialization of the QOS rules. Inspired from
    the Flask project.

    Usually you create a :class:`PyQOS` instance in your main module or
    in the :file:`__init__.py` file of your package like this::
        from pyqos import PyQOS
        app = PyQOS(application_name)
    """
    #: set the main logger in debug mode or not
    debug = ConfigAttribute("DEBUG")
    #: dryrun
    dryrun = ConfigAttribute("DRYRUN")
    #: name of the main logger
    logger_name = ConfigAttribute('LOGGER_NAME')
    #: configuration default values
    default_config = {
        "DEBUG": False,
        "LOGGER_NAME": None,
        "INTERFACES": dict(),
    }

    #: list of qos object to apply at run
    run_list = list()

    def __init__(self, app_name="pyqos", root_path=None):
        self.app_name = app_name
        self.config = Config(root_path, self.default_config)
        self._logger = None
        self.logger_name = self.app_name
        if self.config.get("DEBUG", False):
            _logger.level = logging.DEBUG
        else:
            _logger.level = logging.WARNING

    @property
    def logger(self):
        """
        A :class:`logging.Logger` object for this application.  The
        default configuration is to log to stderr if the application is
        in debug mode.  This logger can be used to (surprise) log messages.
        Here some examples::
            app.logger.debug('A value for debugging')
            app.logger.warning('A warning occurred (%d apples)', 42)
            app.logger.error('An error occurred')
        """
        if self._logger and self._logger.name == self.logger_name:
            if self.config.debug:
                self._logger.level = logging.DEBUG
            else:
                self._logger.level = logging.WARNING
            return self._logger
        self._logger = logging.Logger(
            self.logger_name,
            format="[%(levelname)s] %(message)s (%(filename)s:%(lineno)d) ",
        )
        return self._logger

    def get_ifnames(self, interfaces_lst=None):
        if interfaces_lst is None:
            interfaces_lst = self.config["INTERFACES"]
        if_names = set()
        for interface in interfaces_lst.values():
            if "name" in interface.keys():
                if_names.add(interface["name"])
            else:
                if_names.update(self.get_ifnames(interfaces_lst=interface))
        return if_names

    def run_as_root(self):
        """
        Restart the script as root
        """
        if os.geteuid() != 0:
            print("You need to be root to run this script. Relaunching with "
                  "sudo...\n")
            subprocess.call(["sudo", sys.executable] + sys.argv)
            exit()

    def apply_qos(self):
        self.run_as_root()
        # Clean old rules
        self.reset_qos()
        # Setting new rules
        print("Setting new rules")
        for r in self.run_list:
            r.apply()

    def reset_qos(self):
        """
        Reset QOS for all configured interfaces
        """
        self.run_as_root()
        print("Removing tc rules")
        ifnames = self.get_ifnames()
        tc.qdisc_del(ifnames, stderr=subprocess.DEVNULL)

    def show_qos(self):
        ifnames = self.get_ifnames()
        print("\n\t QDiscs details\n\t================\n")
        tc.qdisc_show(ifnames, "details")
        print("\n\t QDiscs stats\n\t==============\n")
        tc.qdisc_show(ifnames, "details")

    def init_parser(self):
        """
        Init argparse objects
        """
        parser = argparse.ArgumentParser(
            description="Script to set, show or delete QoS rules with TC"
        )

        # Start/Stop/Show command
        sp_action = parser.add_subparsers()
        sp_start = sp_action.add_parser("start", help="set QoS rules")
        sp_stop = sp_action.add_parser("stop", help="Remove all QoS rules")
        sp_show = sp_action.add_parser("show", help="Show QoS rules")

        # Set function to call for each options
        sp_start.set_defaults(func=self.apply_qos)
        sp_stop.set_defaults(func=self.reset_qos)
        sp_show.set_defaults(func=self.show_qos)

        # Debug option
        parser.add_argument('-d', '--debug', help="Set the debug level",
                            dest="debug", action="store_true")
        parser.add_argument('-D', '--dryrun', help="Dry run",
                            dest="dryrun", action="store_true")

        self.arg_parser = parser

    def run(self):
        self.init_parser()

        # If no argument provided show help
        if len(sys.argv) == 1:
            self.arg_parser.print_help()
            sys.exit(1)

        # Parse argument
        args = self.arg_parser.parse_args()

        self.config["DRYRUN"] = args.dryrun
        if args.debug or args.dryrun:
            self.config["DEBUG"] = True

        # Execute correct function, or print usage
        args.func()
