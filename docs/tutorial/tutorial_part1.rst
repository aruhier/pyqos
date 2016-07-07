.. _tutorial_part1:

Part 1: Create the skeleton of your application
===============================================

Before starting, make sure you have installed the framework first. Then,
wherever you want, create a folder that will contain your application. Here,
like in the repository, we will name this folder ``example``.

.. contents:: Table of Contents
   :depth: 2


Defining a configuration
------------------------

Before starting, you should create a configuration for your app. The one in
``example`` should not match to your setup, but is more here to show the
different possibilities it offers.

A more classic configuration might be::

    INTERFACES = {
        "public_if": {  # network card which has the public IP
            "name": "eth0",  # real interface name
            "if_speed": 1048576,  # interface speed, in kbits (here, 1Gbps)
            "speed": 5000,  # Upload speed, for trafic to the Internet
        },

        "lan_if": {  # network card for the LAN subnets
            "name": "eth1",  # real interface name
            "if_speed": 1048576,  # interface speed, in kbits (here, 1Gbps)
            "speed": 100000,  # Download speed, for trafic from the Internet
        },
    }

    DEBUG = False
    DRYRUN = False

``if_speed`` is not obligatory, however it can be useful if you want to combine
an inter-vlan routing with the shaping for your internet connection.

Change the interfaces name (`eth0` and `eth1`) depending of your setup. Here,
``public_if`` corresponds to the interface where and from the internet traffic
is routed, and ``lan_if`` corresponds to the network interface where the LAN
is. In case you have sub interfaces on ``lan_if``, you can let the real
interface name so all your subnets will share the same bandwidth (defined in
``speed``). However, you are also shaping the intervlan routing, so you have to
cheat a bit to avoid this secondary effect.

Save it as ``config.py`` in your application root directory.


Initialize your application
---------------------------

As we are going to define QoS rules in this app, I originally called ``rules``
the folder containing them. Maybe you feel yourself more inspired, so you are
free to choose its name.

Create this ``rules`` folder, and create a file ``__init__.py`` containing::

    from pyqos import PyQoS
    import config

    app = PyQoS()
    app.config.from_object(config)

It just initializes a PyQoS application, and load the configuration file you
wrote during the previous step. You can use PyQoS without using the application
object and manually apply all your rules, however it embeds some easy tools to
really concentrate yourself on your QoS and not on the rest, so you might want
to keep it.

In order to use this app, create a file ``run.py`` in the root of ``example``::

    #!/usr/bin/env python3

    from rules import app

    if __name__ == '__main__':
        app.run()

Then launch ``run.py``::

    $ python3 run.py -h

    usage: run.py [-h] [-d] [-D] {start,stop,show} ...

    Tool to set, show or delete QoS rules on Linux

    positional arguments:
      {start,stop,show}
        start            set QoS rules
        stop             remove all QoS rules
        show             show QoS rules

    optional arguments:
      -h, --help         show this help message and exit
      -d, --debug        set the debug level
      -D, --dryrun       dry run

`Stop` resets all qdiscs on every interfaces declared in your configuration.
`Start` first calls ``stop`` to be sure that any other external rule is
conflicting, and then recursively calls ``apply()`` on every rules attached to
``app``.  `Show` just prints the tc statistics of all your interfaces.
