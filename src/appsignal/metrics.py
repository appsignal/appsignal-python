from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from opentelemetry.metrics import (
    CallbackOptions,
    Histogram,
    Observation,
    UpDownCounter,
    get_meter,
)


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


_gauges: dict[str, dict[TagsKey, int | float]] = {}


def _create_gauge(name: str) -> None:
    def gauge_callback(options: CallbackOptions) -> Iterable[Observation]:
        gauge_entries = _gauges.get(name)
        if gauge_entries is None:
            return []

        observations = []
        for key, value in gauge_entries.items():
            tags = None if key is None else dict(key)

            observations.append(Observation(value, tags))

        _gauges[name] = {}

        return observations

    _meter.create_observable_gauge(
        name,
        callbacks=[gauge_callback],
    )


def set_gauge(name: str, value: float, tags: Tags = None) -> None:
    if name not in _gauges:
        # Create dict for every tag combination
        _gauges[name] = {}
        _create_gauge(name)

    key = (frozenset(tags.items())) if tags is not None else None

    _gauges[name][key] = value
