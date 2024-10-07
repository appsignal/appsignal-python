from __future__ import annotations

from time import time

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
  from typing import Literal, Optional, Union, Self, List

EventKind = Union[Literal["start"], Literal["finish"]]

EventCheckInType = Union[Literal["cron"], Literal["heartbeat"]]

class Event(TypedDict):
    identifier: str
    digest: Optional[str]
    kind: Optional[EventKind]
    timestamp: int
    check_in_type: EventCheckInType

    def __init__(self, **kwargs: Event) -> None:
      super().__init__(**{
        **kwargs,
        "timestamp": int(time())
      })
    
    @classmethod
    def cron(cls, identifier: str, digest: str, kind: EventKind) -> Self:
      return cls(
        identifier=identifier,
        digest=digest,
        kind=kind,
        check_in_type="cron"
      )
    
    @classmethod
    def heartbeat(cls, identifier: str) -> Self:
      return cls(
        identifier=identifier,
        check_in_type="heartbeat"
      )

    def is_redundant(self, other: Self) -> bool:
      if (
        self["check_in_type"] not in ["cron", "heartbeat"] or
        self["check_in_type"] != other["check_in_type"] or
        self["identifier"] != other["identifier"]
      ):
        return False

      if self["check_in_type"] == "cron" and (
        self["digest"] != other["digest"] or
        self["kind"] != other["kind"]
      ):
        return False
      
      return True
    
    @classmethod
    def describe(cls, events: List[Self]) -> str:
      if not events:
        # This shouldn't happen.
        return "no check-in events"
      elif len(events) > 1:
        return f"{len(events)} check-in events"
      else:
        event = events[0]
        if event["check_in_type"] == "cron":
          return (
            f"cron check-in `{event.get('identifier', 'unknown')}` "
            f"{event.get('kind', 'unknown')} event "
            f"(digest {event.get('digest', 'unknown')})"
          )
        elif event["check_in_type"] == "heartbeat":
          return f"heartbeat check-in `{event.get('identifier', 'unknown')}` event"
        else:
          # This shouldn't happen.
          return "unknown check-in event"
