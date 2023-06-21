from abc import ABC, abstractmethod

from typing import Optional


class AppsignalCLICommand(ABC):
    @abstractmethod
    def run(self) -> int:
        raise

    _push_api_key: Optional[str]
    _name: Optional[str]

    def _input_push_api_key(self):
        key = input("Please enter your Push API key: ")
        self._push_api_key = key
        if self._push_api_key == "":
            self._input_push_api_key()

    def _input_name(self):
        self._name = input("Please enter the name of your application: ")
        if self._name == "":
            self._input_name()
