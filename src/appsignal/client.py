from __future__ import annotations

from typing import TYPE_CHECKING

from . import internal_logger as logger
from .binary import NoopBinary
from .config import Config, Options
from .opentelemetry import start as start_opentelemetry
from .probes import start as start_probes


if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .binary import Binary


_client: Client | None = None


def _reset_client() -> None:
    global _client
    _client = None


class Client:
    _config: Config
    _binary: Binary

    def __init__(self, **options: Unpack[Options]) -> None:
        global _client

        self._config = Config(options)
        self._binary = NoopBinary()
        _client = self

    @classmethod
    def config(cls) -> Config | None:
        if _client is None:
            return None

        return _client._config

    def start(self) -> None:
        self._set_binary()

        if self._config.is_active():
            logger.info("Starting AppSignal")
            self._binary.start(self._config)
            if not self._binary.active:
                return
            start_opentelemetry(self._config)
            self._start_probes()
        else:
            logger.info("AppSignal not starting: no active config found")

    def stop(self) -> None:
        from .check_in.scheduler import scheduler

        logger.info("Stopping AppSignal")
        scheduler().stop()
        self._binary.stop(self._config)

    def _start_probes(self) -> None:
        if self._config.option("enable_minutely_probes"):
            start_probes()

    def _set_binary(self) -> None:
        if self._config.should_use_external_collector():
            # When a custom collector endpoint is set, use a `NoopBinary`
            # set to active, so that OpenTelemetry and probes are started,
            # but the agent is not started.
            logger.info(
                "Not starting the AppSignal agent: using collector endpoint instead"
            )
            self._binary = NoopBinary(active=True)
        else:
            # Use the agent when a custom collector endpoint is not set.
            from .agent import Agent

            self._binary = Agent()
