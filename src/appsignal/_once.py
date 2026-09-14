from __future__ import annotations

from typing import Any, Callable

from . import internal_logger as logger


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
