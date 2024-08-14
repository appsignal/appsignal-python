from __future__ import annotations

from typing import Any, Callable, TypeVar

from . import internal_logger as logger
from .check_in import Cron, cron


T = TypeVar("T")


class _Once:
    def __init__(self, func: Callable[..., None], *args: Any, **kwargs: Any) -> None:
        self.called = False
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> None:
        if not self.called:
            self.called = True
            self.func(*self.args, **self.kwargs)

    def reset(self) -> None:
        self.called = False


def _warn_logger_and_stdout(msg: str) -> None:
    logger.warning(msg)
    print(f"appsignal WARNING: {msg}")


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
