#!/usr/bin/python
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


# To be backport compatible
UPLOAD = INTERFACES["public_if"]["speed"]
DOWNLOAD = INTERFACES["lan_if"]["speed"]

# If enabled, this script will not execute any command, just prints it (can be
# override with the -d parameter when launching the script)
DEBUG = False
