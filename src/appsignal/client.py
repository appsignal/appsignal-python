from __future__ import annotations
from typing import TYPE_CHECKING
from .agent import start_agent
from .opentelemetry import start_opentelemetry
from .config import Config, Options

if TYPE_CHECKING:
    from typing import Unpack


class Client:
    _config: Config

    def __init__(self, **options: Unpack[Options]):
        self._config = Config(options)

    def start(self):
        if self._config.option("active"):
            start_agent(self._config)
            start_opentelemetry(self._config)
