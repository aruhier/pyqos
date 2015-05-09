#!/usr/bin/python
# Author: Anthony Ruhier
# Magic formulas for QoS


def burst_formula(rate):
    """
    Cisco formula customized to calculates the burst

    :param rate: rate of the class for the burst to calculate
    """
    return 0.5 * rate/8


def cburst_formula(rate, burst):
    """
    Cisco formula customized to calculates the cburst

    :param rate: rate of the class
    :param burst: burst of the class
    """
    return 1.5 * rate/8 + burst
