#!/usr/bin/python
# Author: Anthony Ruhier
# Magic formulas for QoS


def burst_formula(obj):
    """
    Cisco formula customized to calculates the burst

    :param obj: object to target. Get the rate value from it.
    """
    return 0.5 * obj.rate/8


def cburst_formula(obj):
    """
    Cisco formula customized to calculates the cburst

    :param obj: object to target. Get the rate and burst values from it.
    """
    return 1.5 * obj.rate/8 + obj.burst
