from __future__ import annotations

from abc import ABC, abstractmethod


class AppsignalCLICommand(ABC):
    @abstractmethod
    def run(self) -> int:
        raise NotImplementedError

    _push_api_key: str | None
    _name: str | None

    def _input_push_api_key(self) -> None:
        key = input("Please enter your Push API key: ")
        self._push_api_key = key
        if self._push_api_key == "":
            self._input_push_api_key()

    def _input_name(self) -> None:
        self._name = input("Please enter the name of your application: ")
        if self._name == "":
            self._input_name()
