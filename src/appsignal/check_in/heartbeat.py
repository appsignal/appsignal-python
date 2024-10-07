from __future__ import annotations

from threading import Event, Thread

from .event import heartbeat as heartbeat_event
from .scheduler import scheduler


_HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS = 30.0


def _heartbeat_continuous_interval_seconds() -> float:
    return _HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS


def _set_heartbeat_continuous_interval_seconds(seconds: float) -> None:
    global _HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS
    _HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS = seconds


def _reset_heartbeat_continuous_interval_seconds() -> None:
    global _HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS
    _HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS = 30.0


_started_continuous_heartbeats: list[tuple[Event, Thread]] = []


def _kill_continuous_heartbeats() -> None:
    for event, thread in _started_continuous_heartbeats:
        event.set()
        thread.join()

    _started_continuous_heartbeats.clear()


def _start_continuous_heartbeat(name: str) -> None:
    kill = Event()

    def _run_continuous_heartbeat() -> None:
        while True:
            if kill.wait(_heartbeat_continuous_interval_seconds()):
                break

            heartbeat(name)

    thread = Thread(target=_run_continuous_heartbeat)
    thread.start()
    _started_continuous_heartbeats.append((kill, thread))


def heartbeat(name: str, continuous: bool = False) -> None:
    if continuous:
        _start_continuous_heartbeat(name)

    scheduler().schedule(heartbeat_event(name))
