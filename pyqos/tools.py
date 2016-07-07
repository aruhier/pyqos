#!/usr/bin/env python3
# Author: Anthony Ruhier

from fcntl import ioctl
import logging
import socket
import subprocess
import struct

_logger = logging.getLogger(__name__)


def get_mtu(ifname):
    """
    Use socket ioctl call to get MTU size of an interface
    """
    SIOCGIFMTU = 0x8921
    s = socket.socket(type=socket.SOCK_DGRAM)
    ifr = ifname + '\x00'*(32-len(ifname))
    try:
        ifs = ioctl(s, SIOCGIFMTU, ifr)
        mtu = struct.unpack('<H', ifs[16:18])[0]
    except Exception:
        _logger.warning("Cannot find the MTU of %s. Will use 1500", ifname)
        mtu = 1500
    return mtu


def launch_command(command, stderr=None, dryrun=False):
    """
    If the script is launched in debug mode, just prints the command.
    Otherwise, starts it with subprocess.call()
    """
    _logger.debug(" ".join(command))
    if dryrun:
        return
    r = subprocess.call(command, stderr=stderr)
    if r != 0:
        if stderr == subprocess.DEVNULL:
            return
        _logger.error(" ".join(command))


def get_child_qdiscid(classid):
    """
    Return the id to handle for a child qdisc. By convention, it will take its
    parent class id

    :param classid: parent class id
    """
    return classid[classid.find(":") + 1:]
