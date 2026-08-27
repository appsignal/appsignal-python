from __future__ import annotations

from inspect import signature
from threading import Event, Lock, Thread
from time import gmtime
from typing import Any, Callable, Optional, TypeVar, Union, cast

from . import internal_logger as logger


T = TypeVar("T")

Probe = Union[Callable[[], None], Callable[[Optional[T]], Optional[T]]]

# How long to wait for the probe thread to finish when stopping. Setting the
# stop event wakes the thread immediately, so it only takes this long when a
# probe is running, because the thread cannot finish until that probe returns.
STOP_TIMEOUT_SECONDS = 1.0

_probes: dict[str, Probe] = {}
_probe_states: dict[str, Any] = {}
_lock: Lock = Lock()
_thread: Thread | None = None
_stop_event: Event = Event()


def start() -> None:
    global _thread
    if _thread is None:
        _thread = Thread(target=_minutely_loop, daemon=True)
        _thread.start()


def _minutely_loop() -> None:
    wait_time = _initial_wait_time()

    while True:
        if _stop_event.wait(timeout=wait_time):
            break

        _run_probes()
        wait_time = _wait_time()


def _run_probes() -> None:
    with _lock:
        for name in _probes:
            _run_probe(name)


def _run_probe(name: str) -> None:
    logger.debug(f"Gathering minutely metrics with `{name}` probe")

    try:
        probe = _probes[name]

        if len(signature(probe).parameters) > 0:
            probe = cast(Callable[[Any], Any], probe)
            state = _probe_states.get(name)
            result = probe(state)
            _probe_states[name] = result
        else:
            probe = cast(Callable[[], None], probe)
            probe()

    except Exception as e:
        logger.debug(f"Error in minutely probe `{name}`: {e}")


def _wait_time() -> int:
    return 60 - gmtime().tm_sec


def _initial_wait_time() -> int:
    remaining_seconds = _wait_time()
    if remaining_seconds > 30:
        return remaining_seconds

    return remaining_seconds + 60


def register(name: str, probe: Probe) -> None:
    with _lock:
        if name in _probes:
            logger.debug(
                f"A probe with the name `{name}` is already "
                "registered. Overwriting the entry with the new probe."
            )

        _probes[name] = probe


def unregister(name: str) -> None:
    with _lock:
        if name in _probes:
            del _probes[name]
        if name in _probe_states:
            del _probe_states[name]


def stop() -> None:
    global _thread
    if _thread is None:
        return

    _stop_event.set()
    _thread.join(timeout=STOP_TIMEOUT_SECONDS)

    if _thread.is_alive():
        # Leave the stop event set and the thread in place. The thread breaks
        # out of its loop as soon as the probe it is running returns, and
        # clearing the event here would send it back to waiting instead.
        logger.warning(
            "Timed out waiting for the minutely probes to stop. A probe is "
            "taking longer to run than AppSignal waits for it. Avoid blocking "
            "for long periods inside a minutely probe function."
        )
        return

    _thread = None
    _stop_event.clear()


def clear() -> None:
    with _lock:
        _probes.clear()
        _probe_states.clear()
