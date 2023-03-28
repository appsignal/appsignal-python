from __future__ import annotations
from typing import TYPE_CHECKING
from .agent import start_agent
from .config import from_system, from_public_environ
from .opentelemetry import start_opentelemetry

if TYPE_CHECKING:
    from typing import Unpack
    from .config import Options


class Client:
    _options: Options

    def __init__(self, **options: Unpack[Options]):
        self._options = from_system() | from_public_environ() | options

    def start(self):
        start_agent(self._options)
        start_opentelemetry(self._options)
