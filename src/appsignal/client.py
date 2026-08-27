from __future__ import annotations

from typing import TYPE_CHECKING

from . import internal_logger as logger
from .agent import Agent
from .config import Config, Options
from .opentelemetry import start as start_opentelemetry
from .opentelemetry import stop as stop_opentelemetry
from .probes import start as start_probes
from .probes import stop as stop_probes


if TYPE_CHECKING:
    from typing_extensions import Unpack


_client: Client | None = None


def _reset_client() -> None:
    global _client
    _client = None


class Client:
    _config: Config
    _agent: Agent

    def __init__(self, **options: Unpack[Options]) -> None:
        global _client

        self._config = Config(options)
        self._agent = Agent()
        _client = self

    @classmethod
    def config(cls) -> Config | None:
        if _client is None:
            return None

        return _client._config

    def start(self) -> None:
        if self._config.is_active():
            logger.info("Starting AppSignal")
            self._config.warn()
            self._agent.start(self._config)
            if not self._agent.active:
                # Without the agent there is nothing to send trace data to,
                # unless a collector receives it instead.
                if not self._config.should_use_collector():
                    return
                logger.warning(
                    "The AppSignal agent did not start. Host metrics, NGINX "
                    "metrics, StatsD metrics and environment metadata will "
                    "not be reported."
                )
            start_opentelemetry(self._config)
            self._start_probes()
        else:
            logger.info("AppSignal not starting: no active config found")

    def stop(self) -> None:
        from .check_in.scheduler import scheduler

        logger.info("Stopping AppSignal")
        scheduler().stop()
        # Stop the probes before shutting OpenTelemetry down. Probes report
        # through the metric helpers, which write to the meter provider, so a
        # probe running after it is shut down has nowhere to put its metrics.
        stop_probes()
        # Flush the OpenTelemetry data before stopping the agent. When the
        # agent is used, it is the endpoint that data is sent to, so it must
        # still be running to receive it.
        stop_opentelemetry()
        if self._agent.active:
            self._agent.stop(self._config)

    def _start_probes(self) -> None:
        if self._config.option("enable_minutely_probes"):
            start_probes()
