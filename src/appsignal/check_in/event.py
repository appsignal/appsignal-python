from __future__ import annotations

from time import time
from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired


EventKind = Union[Literal["start"], Literal["finish"]]

EventCheckInType = Union[Literal["cron"], Literal["heartbeat"]]


class Event(TypedDict):
    identifier: str
    digest: NotRequired[str]
    kind: NotRequired[EventKind]
    timestamp: int
    check_in_type: EventCheckInType


def cron(identifier: str, digest: str, kind: EventKind) -> Event:
    return Event(
        identifier=identifier,
        digest=digest,
        kind=kind,
        timestamp=int(time()),
        check_in_type="cron",
    )


def heartbeat(identifier: str) -> Event:
    return Event(
        identifier=identifier, timestamp=int(time()), check_in_type="heartbeat"
    )


def is_redundant(event: Event, existing_event: Event) -> bool:
    if (
        event["check_in_type"] not in ["cron", "heartbeat"]
        or event["check_in_type"] != existing_event["check_in_type"]
        or event["identifier"] != existing_event["identifier"]
    ):
        return False

    if event["check_in_type"] == "cron" and (  # noqa: SIM103
        event.get("digest") != existing_event.get("digest")
        or event.get("kind") != existing_event.get("kind")
    ):
        return False
    return True


def describe(events: list[Event]) -> str:
    if not events:
        # This shouldn't happen.
        return "no check-in events"
    if len(events) > 1:
        return f"{len(events)} check-in events"

    event = events[0]
    if event["check_in_type"] == "cron":
        return (
            f"cron check-in `{event.get('identifier', 'unknown')}` "
            f"{event.get('kind', 'unknown')} event "
            f"(digest {event.get('digest', 'unknown')})"
        )
    if event["check_in_type"] == "heartbeat":
        return f"heartbeat check-in `{event.get('identifier', 'unknown')}` event"

    # This shouldn't happen.
    return "unknown check-in event"  # type: ignore[unreachable]
