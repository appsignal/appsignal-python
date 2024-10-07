from __future__ import annotations

from queue import Queue
from threading import Event as ThreadEvent
from threading import Lock, Thread
from typing import cast

from .. import internal_logger as logger
from ..client import Client
from ..config import Config
from ..transmitter import transmit
from .event import Event, describe, is_redundant


class Scheduler:
    events: list[Event]
    lock: Lock
    queue: Queue
    stopped: bool
    thread: Thread | None
    waker: ThreadEvent | None
    _transmitted: int

    INITIAL_DEBOUNCE_SECONDS: float = 0.1
    BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS: float = 10.0

    def __init__(self) -> None:
        self.lock = Lock()
        self.thread = None
        self.queue = Queue()
        self.stopped = False
        self.events = []
        self.waker = None
        self._transmitted = 0

    def schedule(self, event: Event) -> None:
        config = Client.config()
        if config is None or not config.is_active():
            logger.debug(
                f"Cannot transmit {describe([event])}: AppSignal is not active"
            )
            return

        with self.lock:
            if self.stopped:
                logger.debug(
                    f"Cannot transmit {describe([event])}: AppSignal is stopped"
                )
                return

            self._add_event(event)
            if self.waker is None:
                self._start_waker(self.INITIAL_DEBOUNCE_SECONDS)

            logger.debug(f"Scheduling {describe([event])} to be transmitted")

            if self.thread is None:
                self.thread = Thread(target=self._run)
                self.thread.start()

    def stop(self) -> None:
        with self.lock:
            self._push_events()
            self.stopped = True
            self._stop_waker()
            if self.thread is not None:
                self.queue.put(None)
                self.thread.join()
                self.thread = None

    def _run(self) -> None:
        while True:
            events = self.queue.get()
            if events is None:
                break
            self._transmit(events)
            self._transmitted += 1

    def _transmit(self, events: list[Event]) -> None:
        description = describe(events)

        try:
            response = transmit(
                f"{cast(Config, Client.config()).option('logging_endpoint')}"
                "/check_ins/json",
                ndjson=events,
            )

            if 200 <= response.status_code <= 299:
                logger.debug(f"Transmitted {description}")
            else:
                logger.error(
                    f"Failed to transmit {description}: "
                    f"{response.status_code} status code"
                )
        except Exception as e:
            logger.error(f"Failed to transmit {description}: {e}")

    # Must be called from within a `with self.lock` block.
    def _add_event(self, event: Event) -> None:
        self.events = [
            existing_event
            for existing_event in self.events
            if not is_redundant(event, existing_event)
        ]

        self.events.append(event)

    def _run_waker(self, debounce: float, kill: ThreadEvent) -> None:
        if kill.wait(debounce):
            return
        with self.lock:
            self.waker = None
            self._push_events()

    # Must be called from within a `with self.lock` block.
    def _start_waker(self, debounce: float) -> None:
        self._stop_waker()

        kill = ThreadEvent()
        thread = Thread(target=self._run_waker, args=(debounce, kill))
        thread.start()
        self.waker = kill

    # Must be called from within a `with self.lock` block.
    def _stop_waker(self) -> None:
        if self.waker is not None:
            kill = self.waker
            kill.set()
            self.waker = None

    # Must be called from within a `with self.lock` block.
    def _push_events(self) -> None:
        if not self.events:
            return
        self.queue.put(self.events.copy())
        self.events.clear()
        self._start_waker(self.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS)


_scheduler = Scheduler()


def scheduler() -> Scheduler:
    return _scheduler


def _reset_scheduler() -> None:
    global _scheduler
    _scheduler.stop()
    _scheduler = Scheduler()
    Scheduler.INITIAL_DEBOUNCE_SECONDS = 0.1
    Scheduler.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS = 10.0
