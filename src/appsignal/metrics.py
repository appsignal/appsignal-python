from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry.metrics import Histogram, UpDownCounter, _Gauge, get_meter


if TYPE_CHECKING:
    Tags = dict[str, str | int | float | bool] | None
    TagsKey = frozenset[Any] | None

_meter = get_meter("appsignal-helpers")
_counters: dict[str, UpDownCounter] = {}


def increment_counter(name: str, value: int | float, tags: Tags = None) -> None:
    if name in _counters:
        counter = _counters[name]
    else:
        counter = _meter.create_up_down_counter(name)
        _counters[name] = counter

    counter.add(value, tags)


_histograms: dict[str, Histogram] = {}


def add_distribution_value(name: str, value: int | float, tags: Tags = None) -> None:
    if name in _histograms:
        histogram = _histograms[name]
    else:
        histogram = _meter.create_histogram(name)
        _histograms[name] = histogram

    histogram.record(value, tags)


_gauges: dict[str, _Gauge] = {}


def set_gauge(name: str, value: float, tags: Tags = None) -> None:
    if name in _gauges:
        gauge = _gauges[name]
    else:
        gauge = _meter.create_gauge(name)
        _gauges[name] = gauge

    gauge.set(value, tags)
