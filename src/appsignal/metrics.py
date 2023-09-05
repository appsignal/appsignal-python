from __future__ import annotations


from opentelemetry.metrics import UpDownCounter, get_meter


Tags = None | dict[str, str]

_meter = get_meter("appsignal-helpers")
_counters: dict[str, UpDownCounter] = {}


def increment_counter(name: str, value: int | float, tags: Tags = None) -> None:
    if name in _counters:
        counter = _counters[name]
    else:
        counter = _meter.create_up_down_counter(name)
        _counters[name] = counter

    counter.add(value, tags)
