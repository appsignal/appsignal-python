from __future__ import annotations

from typing import Any, Callable, TypeVar

from ._once import _Once, _warn_logger_and_stdout
from .check_in import Cron, cron


T = TypeVar("T")


_heartbeat_helper_warning = _Once(
    _warn_logger_and_stdout,
    "The helper `heartbeat` has been deprecated. "
    "Please update uses of the helper `heartbeat(...)` to `cron(...)`, "
    "importing it as `from appsignal.check_in import cron`, "
    "in order to remove this message.",
)

_heartbeat_class_warning = _Once(
    _warn_logger_and_stdout,
    "The class `Heartbeat` has been deprecated. "
    "Please update uses of the class `Heartbeat(...)` to `Cron(...)`, "
    "importing it as `from appsignal.check_in import Cron`, "
    "in order to remove this message.",
)


def heartbeat(name: str, fn: Callable[[], T] | None = None) -> None | T:
    _heartbeat_helper_warning()
    return cron(name, fn)


class _MetaHeartbeat(type):
    def __instancecheck__(cls, other: Any) -> bool:
        _heartbeat_class_warning()
        return isinstance(other, Cron)


class Heartbeat(metaclass=_MetaHeartbeat):
    def __new__(cls, name: str) -> Cron:  # type: ignore[misc]
        _heartbeat_class_warning()
        return Cron(name)
