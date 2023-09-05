from opentelemetry.metrics import CallbackOptions, UpDownCounter

from appsignal.metrics import _counters, increment_counter


def test_increment_counter_creates_new_counter():
    assert _counters.get("metric_name") is None

    increment_counter("metric_name", 1)

    assert isinstance(_counters["metric_name"], UpDownCounter)


def test_increment_counter_creates_updates_existing_counter(mocker):
    increment_counter("metric_name", 1)

    counter_spy = mocker.spy(_counters["metric_name"], "add")
    increment_counter("metric_name", 1)

    counter_spy.assert_called_once_with(1, None)


def test_increment_counter_with_tags(mocker):
    increment_counter("metric_name", 1)

    counter_spy = mocker.spy(_counters["metric_name"], "add")

    increment_counter("metric_name", 1, {"tag1": "value1"})

    counter_spy.assert_called_once_with(1, {"tag1": "value1"})
