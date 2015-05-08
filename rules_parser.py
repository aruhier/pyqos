#!/usr/bin/python
# Author: Thomas Gagneret
# Rules parser

from pyparsing import (
    Word, OneOrMore, Group, ZeroOrMore, dictOf, Suppress, alphanums, Keyword,
    restOfLine, Forward
)
from os import path
import sys
import logging

from built_in_classes import *

DIRECTORY = "rules"

__interface__ = "interface"
__leaf__ = "leaf"


class InterfaceParser:
    """ Parse options concerning the root of one interface """

    _root = None

    _content = None
    _interface = None

    algo = None
    default = None
    handle = None
    r2q = None
    quantum = None
    ceil = None
    rate = None
    burst = None
    cburst = None

    def __init__(self, name, content):
        logging.info("New interface %s", name)
        self._interface = name
        self._content = content

        self.parse_options()
        self.create_root()
        self.parse_leaves()

    def create_root(self):
        """
        Create root for this interface
        """
        self._root = RootHTBClass(
            interface=self._interface,
            rate=self.rate,
            ceil=self.ceil,
            burst=self.burst,
            qdisc_prefix_id=str(self.handle) + ":",
            default=self.default,
        )

    def apply_qos(self):
        self._root.apply_qos()

    def parse_options(self):
        """
        Parse interface options
        """
        for option in self._content[0]:
            if hasattr(self, option[0]):
                setattr(self, option[0], option[1])
                logging.info("Set %s to %s", option[0], option[1])
            else:
                logging.warning("Trying to set %s to %s : Unknown keyword",
                                option[0], option[1])

    def parse_leaves(self):
        """
        Parse interface leaves
        """
        # Same level leaf
        for leaf in self._content[1]:
            self._root.add_child(LeafParser(leaf, self.handle).get_leaf())


class LeafParser:
    """
    Parse options in a leaf
    """
    _content = None
    _metaclass = None
    _parent = None

    classid = None
    rate = None
    ceil = None
    burst = None
    cburst = None
    quantum = None
    prio = None
    mark = None
    handle = None
    default = None
    algo = None

    def __init__(self, content, parent):
        logging.info("New leaf")
        self._parent = parent
        self._content = content

        self.parse_options()
        self.set_leaf()
        self.parse_leaves()

    def set_leaf(self):
        if self._content[1]:
            # Generate a subroot
            self._metaclass = ClassRootGenerator(
                classid=self.classid, rate=self.rate, burst=self.burst,
                ceil=self.ceil, cburst=self.cburst, handle=self.handle,
                default=self.default, prio=self.prio, mark=self.mark,
                algorithm=self.algorithm)
        else:
            # Generate end leaf
            self._metaclass = ClassLeafGenerator(
                classid=self.classid, rate=self.rate, burst=self.burst,
                ceil=self.ceil, cburst=self.cburst, prio=self.prio,
                mark=self.mark, algorithm=self.algo)

        self._metaclass = self._metaclass()

    def get_leaf(self):
        return self._metaclass

    def update_properties(self):
        self.classid = str(self._parent) + ":" + str(self.classid)
        self.prio = int(self.prio)
        self.mark = int(self.mark)

    def parse_options(self):
        """
        Parse leaf options
        """
        for option in self._content[0]:
            if hasattr(self, option[0]):
                setattr(self, option[0], option[1])
                logging.info("Set %s to %s", option[0], option[1])
            else:
                logging.warning("Trying to set %s to %s : "
                                "Unknown keyword", option[0], option[1])
        self.update_properties()

    def parse_leaves(self):
        """
        Parse child leaves
        """
        for leaf in self._content[1]:
            self._metaclass.add_child(
                LeafParser(leaf, self.classid).get_leaf()
            )


class RulesParser:
    """
    Get all information in configuration file
    """
    _rules_file = "main"

    _parser = None
    _rules_directory = None
    _interface_struct = None
    _leaf_structure = None

    def __init__(self, directory=DIRECTORY):
        self._leaf_structure = Forward()
        self._rules_directory = directory
        self.set_leaf_parser()
        self.set_interface_parser()
        self._parser = OneOrMore(self._interface_struct)
        self.post_creation()

    def post_creation(self):
        """
        Apply options in parser
        """
        self._parser.ignore("#" + restOfLine)
        # self._parser.setDebug()

    def set_interface_parser(self):
        """
        Set interface structure for parser
        """
        interface_options = Group(ZeroOrMore(Group(
            Word(alphanums) + Word(alphanums))))

        self._interface_struct = (
            Suppress(Keyword(__interface__)) +
            dictOf(
                Word(alphanums),
                (
                    Suppress("{") + interface_options +
                    Group(ZeroOrMore(self._leaf_structure)) +
                    Suppress("}")
                )
            )
        )
        self._parser = None

    def set_leaf_parser(self):
        """
        Set leaf structure for parser
        """
        leaf_options = Group(
            ZeroOrMore(Group(Word(alphanums) + Word(alphanums)))
        )
        leaf_content = leaf_options + Group(ZeroOrMore(self._leaf_structure))

        self._leaf_structure << Suppress(__leaf__) + (
            Suppress("{") +
            Group(leaf_content) +
            Suppress("}")
        )

    def parse(self):
        """
        Parse configuration file
        """
        try:
            return self._parser.parseFile(
                path.join(self._rules_directory, self._rules_file))
        except FileNotFoundError:
            logging.error("File %s not found",
                          path.join(self._rules_directory, self._rules_file))
            return None


class ClassLeafGenerator:
    """
    Create the class according to the leaf properties
    """
    def __new__(cls, classid, prio, mark, rate, ceil, burst, cburst,
                algorithm):
        algorithm = cls.check_algo(algorithm, default=SFQClass)
        leaf = type("leaf", (algorithm,), {})
        leaf.classid = classid
        leaf.prio = prio
        leaf.mark = mark
        leaf.rate = rate
        leaf.ceil = ceil
        leaf.burst = burst
        leaf.cburst = cburst

        return leaf

    def check_algo(algo, default):
        """
        Check if correct algorithm is provided
        """
        if algo is None:
            logging.warning("No algorithm specified. Using default (%s)",
                            default.__name__)
            return default
        else:
            try:
                return globals()[algo + "Class"]
            except KeyError:
                logging.warning("Unknow algorithm specified. Using default %s",
                                default.__name__)
                return default


class ClassRootGenerator:
    """
    Create the class according to the root leaf properties
    """
    def __new__(cls, classid, prio, mark, rate, ceil, burst, cburst, handle,
                default, algorithm):
        algorithm = cls.check_algo(algorithm, default=RootHTBClass)
        root = type("root", (algorithm,), {})
        root.classid = classid
        root.prio = prio
        root.mark = mark
        root.rate = rate
        root.burst = burst
        root.cburst = cburst

        return root

    def check_algo(algo, default):
        """
        Check if correct algorithm is provided
        """
        if algo is None:
            logging.warning("No algorithm specified. Using default (%s)",
                            default.__name__)
            return default
        else:
            try:
                return globals()[algo + "Class"]
            except KeyError:
                logging.warning("Unknow algorithm specified. Using default %s",
                                default.__name__)
                return default

        return None


def get_config(config_file):
    """
    Return parsed configuration
    """
    # Initialize parser
    parser = RulesParser(config_file)

    # Launch parser on config file
    return parser.parse()


def setup_qos(config_file=DIRECTORY):
    """
    Apply Qos from configuration file
    """
    parse_result = get_config(config_file)
    if parse_result is not None:
        if not len(parse_result):
            logging.warning("No interface found in configuration file")
        else:
            # Display extracted information for each interfaces
            for interface in parse_result.keys():
                result = InterfaceParser(interface, parse_result[interface])
                result.apply_qos()


def get_ifnames(config_file=DIRECTORY):
    """
    Return all interfaces found in configuration file
    """
    try:
        return list(get_config(config_file).keys())
    except AttributeError:
        return list()

if __name__ == '__main__':
    log_level = logging.INFO

    logging.basicConfig(
        stream=sys.stderr,
        format="[%(levelname)s] %(message)s ",
        level=log_level
    )

    setup_qos()
