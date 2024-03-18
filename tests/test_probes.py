from time import sleep
from typing import Any, Callable, cast

from appsignal.probes import (
    _probe_states,
    _probes,
    _run_probes,
    register,
    start,
    stop,
    unregister,
)


def test_register(mocker):
    probe = mocker.Mock()
    register("probe_name", probe)

    assert "probe_name" in _probes

    _run_probes()

    probe.assert_called_once()


def test_register_with_state(mocker):
    probe = mocker.Mock()
    probe.return_value = "state"

    register("probe_name", probe)

    assert "probe_name" in _probes

    _run_probes()

    probe.assert_called_once_with(None)
    assert _probe_states["probe_name"] == "state"

    _run_probes()

    probe.assert_called_with("state")


def test_register_signatures():
    # `mocker.Mock` is not used here because we want to test against
    # specific function signatures.

    no_args_called: Any = False
    # An explicit "not called" string is used here because the first
    # call to the probe will pass `None`.
    one_arg_called_with: Any = "not called"
    optional_arg_called_with: Any = "not called"
    many_optional_args_called_with: Any = "not called"
    too_many_args_called: Any = False

    def no_args():
        nonlocal no_args_called
        no_args_called = True

    def one_arg(state):
        nonlocal one_arg_called_with
        one_arg_called_with = state
        return "state"

    def optional_arg(state=None):
        nonlocal optional_arg_called_with
        optional_arg_called_with = state
        return "state"

    def many_optional_args(state, wut=None):
        nonlocal many_optional_args_called_with
        many_optional_args_called_with = state
        return "state"

    # Calling this should fail and log an error, but other probes should
    # still run.
    def too_many_args(state, wut):
        nonlocal too_many_args_called
        # This should not happen.
        too_many_args_called = True

    register("no_args", no_args)
    register("one_arg", one_arg)
    register("optional_arg", optional_arg)
    register("many_optional_args", many_optional_args)
    register("too_many_args", cast(Callable[[], None], too_many_args))

    _run_probes()

    assert no_args_called
    assert one_arg_called_with is None
    assert optional_arg_called_with is None
    assert many_optional_args_called_with is None
    assert not too_many_args_called

    no_args_called = False
    _run_probes()

    assert no_args_called
    assert one_arg_called_with == "state"
    assert optional_arg_called_with == "state"
    assert many_optional_args_called_with == "state"
    assert not too_many_args_called


def test_unregister(mocker):
    probe = mocker.Mock()
    probe.return_value = "state"

    register("probe_name", probe)
    _run_probes()

    unregister("probe_name")
    _run_probes()

    assert "probe_name" not in _probes
    assert "probe_name" not in _probe_states
    probe.assert_called_once_with(None)


def test_start_stop(mocker):
    mocker.patch("appsignal.probes._initial_wait_time").return_value = 0.001
    mocker.patch("appsignal.probes._wait_time").return_value = 0.001

    probe = mocker.Mock()
    register("probe_name", probe)
    start()

    sleep(0.05)

    probe.assert_called()

    stop()
    call_count = probe.call_count

    sleep(0.05)

    assert probe.call_count == call_count
