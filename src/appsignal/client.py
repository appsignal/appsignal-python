from __future__ import annotations

from typing import TYPE_CHECKING

from . import internal_logger as logger
from .agent import agent
from .config import Config, Options
from .opentelemetry import start as start_opentelemetry
from .probes import start as start_probes


if TYPE_CHECKING:
    from typing_extensions import Unpack


_client: Client | None = None


def _reset_client() -> None:
    global _client
    _client = None


class Client:
    _config: Config

    def __init__(self, **options: Unpack[Options]) -> None:
        global _client

        self._config = Config(options)
        _client = self

    @classmethod
    def config(cls) -> Config | None:
        if _client is None:
            return None

        return _client._config

    def start(self) -> None:
        if self._config.is_active():
            logger.info("Starting AppSignal")
            agent.start(self._config)
            if not agent.active:
                return
            start_opentelemetry(self._config)
            self._start_probes()
        else:
            logger.info("AppSignal not starting: no active config found")

    def _start_probes(self) -> None:
        if self._config.option("enable_minutely_probes"):
            start_probes()
