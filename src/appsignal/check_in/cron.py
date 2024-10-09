from __future__ import annotations

from binascii import hexlify
from os import urandom
from typing import Any, Callable, Literal, TypeVar

from .event import cron as cron_event
from .scheduler import scheduler


T = TypeVar("T")


class Cron:
    identifier: str
    digest: str

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.digest = hexlify(urandom(8)).decode("utf-8")

    def start(self) -> None:
        scheduler().schedule(cron_event(self.identifier, self.digest, "start"))

    def finish(self) -> None:
        scheduler().schedule(cron_event(self.identifier, self.digest, "finish"))

    def __enter__(self) -> None:
        self.start()

    def __exit__(
        self, exc_type: Any = None, exc_value: Any = None, traceback: Any = None
    ) -> Literal[False]:
        if exc_type is None:
            self.finish()

        return False


def cron(identifier: str, fn: Callable[[], T] | None = None) -> None | T:
    cron = Cron(identifier)
    output = None

    if fn is not None:
        cron.start()
        output = fn()

    cron.finish()
    return output
