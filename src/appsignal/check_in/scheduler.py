from __future__ import annotations

from threading import Thread, Lock
from queue import Queue
from typing import List, Optional, cast
from time import sleep

from .event import Event
from ..client import Client
from .. import internal_logger as logger
from ..transmitter import transmit

class AcquiredLock:
    def __new__(_cls):
        raise TypeError("AcquiredLock instances cannot be constructed")

class TypedLock(Lock):
    def __enter__(self) -> AcquiredLock:
        super().__enter__()
        return cast(AcquiredLock, None)

class Scheduler:
    events: List[Event]
    lock: TypedLock
    queue: Queue
    stopped: bool
    thread: Optional[Thread]
    waker: Optional[Thread]
    _transmitted: int

    INITIAL_DEBOUNCE_SECONDS = 0.1
    BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS = 10

    def __init__(self):
        self.lock = Lock()
        self.thread = None
        self.queue = Queue()
        self.stopped = False
        self.events = []
        self.waker = None
        self._transmitted = 0

    def schedule(self, event: Event):
        if not Client.config().is_active():
            logger.debug(f"Cannot transmit {Event.describe([event])}: AppSignal is not active")
            return

        with self.lock as locked:
            if self.stopped:
                logger.debug(f"Cannot transmit {Event.describe([event])}: AppSignal is stopped")
                return
            self._add_event(locked, event)
            if self.waker is None:
                self._start_waker(locked, self.INITIAL_DEBOUNCE_SECONDS)

            logger.debug(f"Scheduling {Event.describe([event])} to be transmitted")

            if self.thread is None:
                self.thread = Thread(target=self._run)
                self.thread.start()

    def stop(self):
        with self.lock as locked:
            self._push_events(locked)
            self.stopped = True
            self._stop_waker(locked)
            if self.thread is not None:
                self.thread.join()
                self.thread = None

    def _run(self):
        while True:
            events = self.queue.get()
            if events is None:
                break

            self._transmit(events)
            self.transmitted += 1

    def _transmit(self, events: List[Event]):
        description = Event.describe(events)

        try:
            response = transmit(f"{Client.config().option('logging_endpoint')}/check_ins/json", json=events)

            if 200 <= response.status_code <= 299:
                logger.debug(f"Transmitted {description}")
            else:
                logger.error(f"Failed to transmit {description}: {response.status_code} status code")
        except Exception as e:
            logger.error(f"Failed to transmit {description}: {e}")

    def _add_event(self, locked: AcquiredLock, event: Event):
        self.events = [
            existing_event for existing_event in self.events
            if not event.is_redundant(existing_event)
        ]
        
        self.events.append(event)

    def _run_waker(self, debounce: float):
        sleep(debounce)

        with self.lock as locked:
            self.waker = None
            self._push_events(locked)

    def _start_waker(self, locked: AcquiredLock, debounce: float):
        self._stop_waker(locked)

        self.waker = Thread(debounce, target=self._run_waker, args=(debounce,))
        self.waker.start()

    def _stop_waker(self, locked: AcquiredLock):
        if self.waker is not None:
            self.waker.cancel()
            self.waker = None

    def _push_events(self, locked: AcquiredLock):
        if not self.events:
            return

        self.queue.put(self.events.copy())
        self.events.clear()
        self._start_waker(locked, self.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS)

scheduler = Scheduler()
