.. _quickstart:

==========
Quickstart
==========

.. currentmodule:: pyqos

PyQoS allows you to setup a simple or a complex group of QoS rules, by allowing
to add some intelligences in their relations, but in trying to keep a clear
syntax (making it usable by non python developers). You can see it as a wrapper
for the tool tc, that is used as a backend for now.

Even if PyQoS helps you to set your rules, it requires you to have some
knowledge about how the QoS works (in high level) on Linux, and how to use tc.
This documentation will not explain in detail each algorithm, and it will be a
lot easier to debug if you understand what PyQoS does in the backend.

.. contents:: Table of Contents
   :depth: 3

.. _quickstart_minimal_app:

A minimal application
---------------------

A more split design will certainly be preferred, but to understand the process,
this part will be focused on an application written in only one source file.

First you can create a :class:`PyQoS` object, which is used as the
application's base. This step is optional, but it will handle all the process
of applying each rule and brings a built-in helper so you do not have to
rewrite it. Then, bring to this application object a configuration, which will
mainly be the network interfaces definition.

Once created, the QoS rules can be defined, by using the models in
``pyqos.algorithms``. Then it can be attached to the application::

    from pyqos import PyQoS
    from pyqos.algorithms.htb import RootHTBClass, HTBFilterFQCodel

    app = PyQoS()
    app.config["INTERFACES"] = {
        "public_if": {  # The key will be used as an alias for your interface
            "name": "eth0",  # real interface name
            "if_speed": 1048576,  # interface speed, in kbits (here, 1Gbps)
            "speed": 5000,  # Upload speed, for trafic to the Internet
        },

        "lan_if": {
            "name": "eth1",
            "if_speed": 1048576,
            "speed": 100000,
        },
    }


    class GenericRootHTB(RootHTBClass):
        """
        Generic root htb
        """
        default = 1500  # Default mark


    class HTBChildExample(HTBFilterFQCodel):
        """
        Example that will match on packets that have the mark 200
        """
        id = 200
        prio = 20
        mark = id
        rate = 20000
        ceil = 100000
        burst = rate * 1.5
        cburst = 1.5 * rate/8 + burst


    # Add the 2 rules for each interface defined in the app configuration
    for ifname, val in app.config["INTERFACES"].items():
        root_class = RootHTBClass(
            interface=val["name"], rate=val["speed"],
            burst=val["speed"]/8
        )
        root_class.add_child(HTBChildExample())
        app.run_list.append(root_class)

    if __name__ == '__main__':
        app.run()  # if you want a built-in argparser
        # app.apply_qos()  # if you want to directly apply the rules linked


You can test it by running ``python3 qos_rules.py -D start``, which will
trigger the dry-run mode, and prints the tc commands that would normally be
applied.

For more informations about each algorithm models, you should read the dev_api_
documentation.


.. _quickstart_config:

Split the configuration in its own file
---------------------------------------

The configuration can be split in its own source file, for example
``config.py`` which will be in the root of your application::

    #!/usr/bin/env python3
    # config.py

    # INTERFACES
    INTERFACES = {
        "public_if": {  # The key will be used as an alias for your interface
            "name": "eth0",  # real interface name
            "if_speed": 1048576,  # interface speed, in kbits (here, 1Gbps)
            "speed": 5000,  # Upload speed, for trafic to the Internet
        },

        "lan_if": {
            "name": "eth1",
            "if_speed": 1048576,
            "speed": 100000,
        },
    }

Then import it in your app:

>>> import config
>>> app.config.from_object(config)

or:

>>> app.config.from_pyfile("config.py")

You can read :ref:`the documentation related to the configuration
<config>` for more informations.


.. _quickstart_debug_dryrun:

Debug mode and dry-run
----------------------

As PyQoS uses tc as backend, enabling the debug mode allows you to see which
commands are run. You can also enable the dry run mode, that automatically
enable the debug mode, to not apply the commands.

You can trigger these mods by setting your application attribute:

>>> app.debug = True
>>> app.dryrun = True
>>> app.run()

Or by setting it in your configuration file::

    DEBUG = True
    DRYRUN = True

And you can also do it when you are calling your program::

    $ python3 myapp.py -d -D

These three methods are equivalents.


.. _parental:

Parental
--------

Classful algorithms can have a parent and children, to construct an entire
branch of rules that share some attributes as the network interface, the prefix
class id, etc…

Here is an example of a root HTB class, linked with an HTB class child::

    class HTBChildExample(HTBFilterFQCodel):
        """
        Example that will match on packets that have the mark 200
        """
        id = 200
        prio = 20
        mark = id
        rate = 20000
        ceil = 100000
        burst = rate * 1.5
        cburst = 1.5 * rate/8 + burst


    class GenericRootHTB(RootHTBClass):
        """
        Generic root htb
        """
        default = 1500  # Default mark

        def __init__(*args, **kwargs):
            super().__init__(*args, **kwargs)
            self.add_child(HTBChildExample())


In this example, it set the ``parent`` child's attribute to point on the parent
object.

>>> root_class = RootHTBClass(default=1500)
>>> child_class = HTBChildExample()
>>> root_class.add_child(child_class)
>>> child_class.parent == root_class
True
>>> child_class in root_class.children
True

.. important::
    To add a child, you should not append it manually to the ``children``
    attribute, but always pass by the ``add_child`` function

Classless qdiscs also have a parent attributes, but obviously they do not have
a ``children`` attribute.
