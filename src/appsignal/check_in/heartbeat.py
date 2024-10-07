from .scheduler import scheduler
from .event import Event
from threading import Thread
from time import sleep

_HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS = 30

def _continuous_heartbeat(name: str) -> None:
  while True:
    sleep(_HEARTBEAT_CONTINUOUS_INTERVAL_SECONDS)
    heartbeat(name)

def heartbeat(name: str, continuous: bool = False) -> None:
    if continuous:
        thread = Thread(target=_continuous_heartbeat, args=(name,))
        thread.start()
    scheduler.schedule(Event.heartbeat(name))
