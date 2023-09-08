from __future__ import annotations

from typing import Any

from opentelemetry.metrics import CallbackOptions, UpDownCounter

from appsignal import increment_counter, set_gauge
from appsignal.metrics import _counters, _gauges, _meter


def test_increment_counter_creates_new_counter():
    assert _counters.get("metric_name") is None

    increment_counter("metric_name", 1)

    assert isinstance(_counters["metric_name"], UpDownCounter)


def test_increment_counter_updates_existing_counter(mocker):
    increment_counter("metric_name", 1)

    counter_spy = mocker.spy(_counters["metric_name"], "add")
    increment_counter("metric_name", 1)

    counter_spy.assert_called_once_with(1, None)


def test_increment_counter_with_tags(mocker):
    increment_counter("metric_name", 1)

    counter_spy = mocker.spy(_counters["metric_name"], "add")

    increment_counter("metric_name", 1, {"tag1": "value1"})

    counter_spy.assert_called_once_with(1, {"tag1": "value1"})


def test_set_gauge_creates_new_gauge(mocker):
    meter_spy = mocker.spy(_meter, "create_observable_gauge")
    assert "metric_name" not in _gauges

    set_gauge("metric_name", 10)

    # Registers the gauges internally
    assert _gauges["metric_name"][None] == 10

    # Check if it was registered on the meter
    meter_spy.assert_called_once_with("metric_name", callbacks=mocker.ANY)
    callbacks = meter_spy.call_args.kwargs["callbacks"]
    assert len(callbacks) == 1

    # Mock the ObservableGauge's async task calling the callbacks
    return_values = callbacks[0](CallbackOptions())
    assert len(return_values) == 1
    return_value = return_values[0]
    assert return_value.value == 10
    assert return_value.attributes is None

    # Resets gauge values
    assert _gauges["metric_name"] == {}

    return_values = callbacks[0](CallbackOptions())
    assert len(return_values) == 0


def test_set_gauge_updates_existing_gauge():
    set_gauge("existing", 10)
    set_gauge("existing", 11, None)  # None is also the default

    assert _gauges["existing"][None] == 11

    set_gauge("existing_with_tags", 10, {"tag1": "value1"})
    set_gauge("existing_with_tags", 11, {"tag1": "value1"})

    assert _gauges["existing_with_tags"][tags_key({"tag1": "value1"})] == 11


def test_set_gauge_updates_with_tags(mocker):
    meter_spy = mocker.spy(_meter, "create_observable_gauge")
    set_gauge("with_tags1", 10, {"tag1": "value1"})
    set_gauge("with_tags1", 11, {"tag1": "value1"})
    set_gauge("with_tags1", 55, {"other": "value2"})

    assert _gauges["with_tags1"][tags_key({"tag1": "value1"})] == 11
    assert _gauges["with_tags1"][tags_key({"other": "value2"})] == 55

    # Mock the ObservableGauge's async task calling the callbacks
    callbacks = meter_spy.call_args.kwargs["callbacks"]
    return_values = callbacks[0](CallbackOptions())
    assert len(return_values) == 2

    obs1 = return_values[0]
    assert obs1.value == 11
    assert obs1.attributes == {"tag1": "value1"}

    obs2 = return_values[1]
    assert obs2.value == 55
    assert obs2.attributes == {"other": "value2"}

    # Resets gauge values
    assert _gauges["with_tags1"] == {}

    callbacks = meter_spy.call_args.kwargs["callbacks"]
    return_values = callbacks[0](CallbackOptions())
    assert len(return_values) == 0


def tags_key(tags: dict[str, str]) -> frozenset[Any]:
    return frozenset(tags.items())
