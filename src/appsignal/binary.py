from __future__ import annotations

from abc import ABC, abstractmethod

from .config import Config


class Binary(ABC):
    @property
    @abstractmethod
    def active(self) -> bool: ...

    @abstractmethod
    def start(self, config: Config) -> None: ...

    @abstractmethod
    def stop(self, config: Config) -> None: ...


class NoopBinary(Binary):
    def __init__(self, active: bool = False) -> None:
        self._active = active

    @property
    def active(self) -> bool:
        return self._active

    def start(self, config: Config) -> None:
        pass

    def stop(self, config: Config) -> None:
        pass
