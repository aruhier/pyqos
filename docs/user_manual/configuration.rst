.. _user_man_config:

=============
Configuration
=============

.. currentmodule:: pyqos

PyQoS bring a configuration model very similar to what does Flask (a big part
of their code has been copied here), and helps you to share global variables
with all your rules.

If you did not, you should read this part before continue:
user_man_quickstart_config_.

For this part, we will use this configuration file, originally named `conf.py`,
as an example::

    #!/usr/bin/env python3
    # Author: Anthony Ruhier

    # INTERFACES
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

        "GROUP_EXEMPLE": {  # example of a group of interfaces
            "tap0": {
                "name": "tap0",  # real interface name
                "speed": 10000,  # Speed for trafic from the Internet
            },
            "tap1": {
                "name": "tap1",  # real interface name
            },
        },
    }

    # If we want to get the speed of tap1 equaled to 40% of the lan_if speed
    INTERFACES["GROUP_EXEMPLE"]["tap1"]["speed"] = (
        INTERFACES["public_if"]["speed"] * 0.4)

    DEBUG = False
    DRYRUN = False


.. _user_man_config_needed_var:
Default values
--------------

You are free to add any variables you want and need in your configuration, but
some are used by the PyQoS application. In case you do not use the built-in
application and decide to apply your QoS rules by yourself, you can ignore this
part.

A default configuration is already defined in `PyQoS.app`::

    DEBUG = False
    DRYRUN = False
    INTERFACES = {}

``DEBUG`` and ``DRYRUN`` are detailed :ref:`here
<user_man_quickstart_debug_dryrun>`.

``INTERFACES`` allows you to define different characteristics about the network
interface you have. It is used by `PyQoS.app` during the application start,
because it will reset any QoS on the defined interfaces before applying the new
ones.

Each item in ``INTERFACES`` has to be a dictionary, containing at least one key
``name`` whose the value corresponds to the interface's real name. You can see
the keys in ``INTERFACES`` as aliases for your interfaces, which then target to
their real informations.
