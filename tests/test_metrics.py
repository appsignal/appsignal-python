from __future__ import annotations

from typing import Any
from unittest.mock import call

from opentelemetry.metrics import Histogram, UpDownCounter, _Gauge

from appsignal import add_distribution_value, increment_counter, set_gauge
from appsignal.metrics import _counters, _gauges, _histograms, _meter


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

    increment_counter(
        "metric_name",
        1,
        {"tag1": "value1", "int": 123, "float": 123.456, "true": True, "false": False},
    )

    counter_spy.assert_called_once_with(
        1,
        {"tag1": "value1", "int": 123, "float": 123.456, "true": True, "false": False},
    )


def test_add_distribution_value_creates_new_histogram():
    assert _histograms.get("metric_name") is None

    add_distribution_value("metric_name", 1)

    assert isinstance(_histograms["metric_name"], Histogram)


def test_add_distribution_value_updates_existing_histogram(mocker):
    add_distribution_value("metric_name", 1)

    histogram_spy = mocker.spy(_histograms["metric_name"], "record")
    add_distribution_value("metric_name", 1)

    histogram_spy.assert_called_once_with(1, None)


def test_add_distribution_value_with_tags(mocker):
    add_distribution_value("metric_name", 1)

    histogram_spy = mocker.spy(_histograms["metric_name"], "record")

    add_distribution_value(
        "metric_name",
        1,
        {"tag1": "value1", "int": 123, "float": 123.456, "true": True, "false": False},
    )

    histogram_spy.assert_called_once_with(
        1,
        {"tag1": "value1", "int": 123, "float": 123.456, "true": True, "false": False},
    )


def test_set_gauge_creates_new_gauge(mocker):
    meter_spy = mocker.spy(_meter, "create_gauge")
    assert "metric_name" not in _gauges

    set_gauge("metric_name", 10)

    # Registers the gauges internally
    assert isinstance(_gauges["metric_name"], _Gauge)

    # Check if it was registered on the meter
    meter_spy.assert_called_once_with("metric_name")


def test_set_gauge_updates_existing_gauge(mocker):
    _gauges["existing"] = _meter.create_gauge("existing")
    gauge1_spy = mocker.spy(_gauges["existing"], "set")

    set_gauge("existing", 10)
    set_gauge("existing", 11, None)  # None is also the default

    gauge1_spy.assert_has_calls([call(10, None), call(11, None)])

    _gauges["existing_with_tags"] = _meter.create_gauge("existing_with_tags")
    gauge2_spy = mocker.spy(_gauges["existing_with_tags"], "set")

    set_gauge("existing_with_tags", 10, {"tag1": "value1"})
    set_gauge("existing_with_tags", 11, {"tag1": "value1"})

    gauge2_spy.assert_has_calls(
        [call(10, {"tag1": "value1"}), call(11, {"tag1": "value1"})]
    )


def tags_key(tags: dict[str, str]) -> frozenset[Any]:
    return frozenset(tags.items())
