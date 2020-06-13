
import pytest

import pyqos.backend.tc
from pyqos.backend import tc


NETIF = "eth0"


@pytest.fixture
def fixture_disable_commands(monkeypatch, mocker):
    monkeypatch.setattr("pyqos.backend.tc.launch_command", mocker.stub())
    launch_cmd_spy = pyqos.backend.tc.launch_command

    return launch_cmd_spy


def test_qdisc_root(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qdisc(interface=NETIF, action="add")
    expected_cmd = ["tc", "qdisc", "add", "dev", NETIF, "root"]
    launch_cmd_spy.assert_called_with(expected_cmd, None, False)


def test_qdisc_standard_rule(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qdisc(
        interface=NETIF, action="add", parent="1:0", algorithm="htb",
        handle="10", testopt="test"
    )
    expected_cmd = [
        "tc", "qdisc", "add", "dev", NETIF, "parent", "1:0", "handle", "10",
        "htb", "testopt", "test"
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, None, False)


@pytest.fixture
def fixture_qdisc_wrapper(fixture_disable_commands):
    kwargs = {
        "interface": NETIF, "parent": "2:10", "algorithm": "sfq", "handle":
        "30", "testopt": "test"
    }
    return fixture_disable_commands, kwargs


def test_qdisc_add(fixture_qdisc_wrapper):
    """
    Ensure that qdisc and qdisc_add call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_qdisc_wrapper
    tc.qdisc(action="add", **kwargs)
    tc.qdisc_add(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_qdisc_del(fixture_qdisc_wrapper):
    """
    Ensure that qdisc and qdisc_del call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_qdisc_wrapper
    tc.qdisc(action="delete", **kwargs)
    tc.qdisc_del(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_qdisc_show(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qdisc_show()
    expected_cmd = ["tc", "qdisc", "show"]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


def test_qos_class(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qos_class(interface=NETIF, action="add", parent="1:0")
    expected_cmd = [
        "tc", "class", "add", "dev", NETIF, "parent", "1:0", "htb",
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


def test_qos_class_with_id(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qos_class(
        interface=NETIF, action="add", parent="1:0", classid="1:10",
        algorithm="sfq"
    )
    expected_cmd = [
            "tc", "class", "add", "dev", NETIF, "parent", "1:0", "classid",
            "1:10", "sfq",
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


def test_qos_class_htb_rate_ceil(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qos_class(
        interface=NETIF, action="add", parent="1:0", classid="1:10",
        rate=400, burst=100, ceil=800, cburst=300
    )
    expected_cmd = [
            "tc", "class", "add", "dev", NETIF, "parent", "1:0", "classid",
            "1:10", "htb",
            "burst", str(100 * 1024), "cburst", str(300 * 1024),
            "ceil", str(800 * 1024), "rate", str(400 * 1024),
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


@pytest.fixture
def fixture_qos_class_wrapper(fixture_disable_commands):
    kwargs = {
        "interface": NETIF, "parent": "1:0", "classid": "1:10", "rate": 400,
        "burst": 100, "ceil": 800, "cburst": 300,
    }
    return fixture_disable_commands, kwargs


def test_qos_class_add(fixture_qos_class_wrapper):
    """
    Ensure that qos_class and qos_class_add call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_qos_class_wrapper
    tc.qos_class(action="add", **kwargs)
    tc.qos_class_add(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_qos_class_del(fixture_qos_class_wrapper):
    """
    Ensure that qos_class and qos_class_del call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_qos_class_wrapper
    tc.qos_class(action="delete", **kwargs)
    tc.qos_class_del(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_qos_class_show(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.qos_class_show(interface=NETIF)
    expected_cmd = ["tc", "class", "show", "dev", NETIF]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


def test_filter(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.filter(
        interface=NETIF, action="add", prio=10, handle="1:10", flowid="10"
    )
    expected_cmd = [
        "tc", "filter", "add", "dev", NETIF, "protocol", "all",
        "prio", "10", "handle", "1:10", "fw", "flowid", "10"
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


def test_filter_with_parent(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.filter(
        interface=NETIF, action="add", prio=10, handle="1:10", flowid=10,
        protocol="ip", parent="1:0"
    )
    expected_cmd = [
        "tc", "filter", "add", "dev", NETIF, "parent", "1:0",
        "protocol", "ip", "prio", "10", "handle", "1:10", "fw", "flowid", "10"
    ]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)


@pytest.fixture
def fixture_filter_wrapper(fixture_disable_commands):
    kwargs = {
        "interface": NETIF, "prio": 20, "handle": "1:40",
        "flowid": 10, "protocol": "ip", "parent": "1:0"
    }
    return fixture_disable_commands, kwargs


def test_filter_add(fixture_filter_wrapper):
    """
    Ensure that filter and filter_add call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_filter_wrapper
    tc.filter(action="add", **kwargs)
    tc.filter_add(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_filter_del(fixture_filter_wrapper):
    """
    Ensure that filter and filter_del call the same command at the end
    """
    launch_cmd_spy, kwargs = fixture_filter_wrapper
    tc.filter(action="delete", **kwargs)
    tc.filter_del(**kwargs)

    calls = launch_cmd_spy.call_args_list
    assert calls[0] == calls[1]


def test_filter_show(fixture_disable_commands):
    launch_cmd_spy = fixture_disable_commands

    tc.filter_show(interface=NETIF)
    expected_cmd = ["tc", "filter", "show", "dev", NETIF]
    launch_cmd_spy.assert_called_with(expected_cmd, dryrun=False)
