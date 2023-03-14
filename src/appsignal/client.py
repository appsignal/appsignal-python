from typing import Unpack
from .config import Options


class Client:
    def __init__(self, **options: Unpack[Options]):
        self._options = options

    def start(self):
        print(__file__)
