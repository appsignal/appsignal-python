from __future__ import annotations

from binascii import hexlify
from os import urandom
from time import time
from typing import Any, Callable, Literal, TypedDict, TypeVar, Union

from . import internal_logger as logger
from .client import Client
from .config import Config
from .transmitter import transmit


T = TypeVar("T")

EventKind = Union[Literal["start"], Literal["finish"]]


class Event(TypedDict):
    identifier: str
    digest: str
    kind: EventKind
    timestamp: int
    check_in_type: Literal["cron"]


class Cron:
    identifier: str
    digest: str

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.digest = hexlify(urandom(8)).decode("utf-8")

    def _event(self, kind: EventKind) -> Event:
        return Event(
            identifier=self.identifier,
            digest=self.digest,
            kind=kind,
            timestamp=int(time()),
            check_in_type="cron",
        )

    def _transmit(self, event: Event) -> None:
        config = Client.config() or Config()

        if not config.is_active():
            logger.debug("AppSignal not active, not transmitting cron check-in event")
            return

        url = f"{config.option('logging_endpoint')}/check_ins/json"
        try:
            response = transmit(url, json=event)
            if 200 <= response.status_code <= 299:
                logger.debug(
                    f"Transmitted cron check-in `{event['identifier']}` "
                    f"({event['digest']}) {event['kind']} event"
                )
            else:
                logger.error(
                    f"Failed to transmit cron check-in {event['kind']} event: "
                    f"status code was {response.status_code}"
                )
        except Exception as e:
            logger.error(f"Failed to transmit cron check-in {event['kind']} event: {e}")

    def start(self) -> None:
        self._transmit(self._event("start"))

    def finish(self) -> None:
        self._transmit(self._event("finish"))

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
