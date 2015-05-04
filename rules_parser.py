#!/usr/bin/python
# Author: Thomas Gagneret
# Rules parser

from pyparsing import Word, OneOrMore, oneOf, Group, ZeroOrMore, dictOf, \
    Suppress, alphanums, Keyword, restOfLine, Forward
from os import path
import sys
import logging

__setter__ = "@set"
__define__ = "@def"

__interface__ = "interface"
__leaf__ = "leaf"

__interface_keywords__ = [__setter__]
__leaf_keywords__ = [__setter__]


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

    def __init__(self, name, content):
        logging.info("New interface %s", name)
        self._interface = name
        self._content = content

        self.parse_options()
        self.parse_leaves()

    def parse_options(self):
        """ Parse interface options  """

        for option in self._content[0]:
            if option[0] == __setter__:
                if hasattr(self, option[1]):
                    setattr(self, option[1], option[2])
                    logging.info("%s => %s : %s",
                                 option[0], option[1], option[2])
                else:
                    logging.warning("Trying to set %s to %s : Unknown keyword",
                                    option[1], option[2])
            else:
                logging.warning("Unrecognized keywords %s in interface %s",
                                option[0], self._interface)

    def parse_leaves(self):
        """ Parse interface leaves """

        # Same level leaf
        for leaf in self._content[1]:
            LeafParser(leaf)


class LeafParser:
    """ Parse options in a leaf """

    _content = None

    classid = None
    rate = None
    ceil = None
    burst = None
    cburst = None
    quantum = None
    prio = None
    handle = None
    default = None

    def __init__(self, content):
        logging.info("New leaf")
        self._content = content
        self.parse_options()
        self.parse_leaves()

    def parse_options(self):
        """ Parse leaf options """

        for option in self._content[0]:
            if option[0] == __setter__:
                if hasattr(self, option[1]):
                    setattr(self, option[1], option[2])
                    logging.info("%s => %s : %s",
                                 option[0], option[1], option[2])
                else:
                    logging.warning("Trying to set %s to %s : \
                                        Unknown keyword",
                                    option[1], option[2])
            else:
                logging.warning("Unrecognized keywords %s",
                                option[0])

    def parse_leaves(self):
        """ Parse child leaves """

        for leaf in self._content[1]:
            LeafParser(leaf)


class RulesParser:
    """ Get all information in configuration file """

    _rules_directory = "rules"

    _parser = None
    _rules_file = None
    _interface_struct = None
    _leaf_structure = None

    def __init__(self, config="main"):
        self._leaf_structure = Forward()
        self._rules_file = config
        self.set_leaf_parser()
        self.set_interface_parser()
        self._parser = OneOrMore(self._interface_struct)
        self.post_creation()

    def post_creation(self):
        """ Apply options in parser """

        self._parser.ignore("#" + restOfLine)
        # self._parser.setDebug()

    def set_interface_parser(self):
        """ Set interface structure for parser """

        interface_options = Group(ZeroOrMore(Group(
            oneOf(__interface_keywords__) + Word(alphanums) +
            Word(alphanums))))

        self._interface_struct = Suppress(Keyword(__interface__)) + \
            dictOf(Word(alphanums), Suppress("{") + interface_options +
                   Group(ZeroOrMore(self._leaf_structure)) +
                   Suppress("}"))

        self._parser = None

    def set_leaf_parser(self):
        """ Set leaf structure for parser """

        leaf_options = Group(ZeroOrMore(
            Group(oneOf(__leaf_keywords__) + Word(alphanums) + Word(alphanums))
        ))
        leaf_content = leaf_options + \
            Group(ZeroOrMore(self._leaf_structure))

        self._leaf_structure << Suppress(__leaf__) + \
            Suppress("{") + \
            Group(leaf_content) + \
            Suppress("}")

    def parse(self):
        """ Parse configuration file """

        try:
            return self._parser.parseFile(
                path.join(self._rules_directory, self._rules_file))
        except FileNotFoundError:
            logging.error("File %s not found",
                          path.join(self._rules_directory, self._rules_file))
            return None


if __name__ == '__main__':
    log_level = logging.INFO

    logging.basicConfig(
        stream=sys.stderr,
        format="[%(levelname)s] %(message)s ",
        level=log_level
    )
    # Initialize parser
    parser = RulesParser()

    # Launch parser on config file
    parse_result = parser.parse()

    if parse_result is not None:

        # Display extracted information for each interfaces
        for interface in parse_result.keys():
            result = InterfaceParser(interface, parse_result[interface])
