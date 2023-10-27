from __future__ import annotations

import os
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from functools import cached_property


@dataclass(frozen=True)
class AppsignalCLICommand(ABC):
    args: Namespace

    @staticmethod
    @abstractmethod
    def init_parser(parser: ArgumentParser) -> None:
        pass

    @staticmethod
    def _push_api_key_argument(parser: ArgumentParser) -> None:
        parser.add_argument(
            "--push-api-key",
            default=os.environ.get("APPSIGNAL_PUSH_API_KEY"),
            help="Push API Key",
        )

    @staticmethod
    def _application_argument(parser: ArgumentParser) -> None:
        parser.add_argument(
            "--application",
            default=os.environ.get("APPSIGNAL_APP_NAME"),
            help="Application name",
        )

    @staticmethod
    def _environment_argument(parser: ArgumentParser) -> None:
        parser.add_argument(
            "--environment",
            default=os.environ.get("APPSIGNAL_APP_ENV"),
            help="App environment",
        )

    @abstractmethod
    def run(self) -> int:
        raise NotImplementedError

    @cached_property
    def _push_api_key(self) -> str | None:
        key = self.args.push_api_key
        while not key:
            key = input("Please enter your Push API key: ")
        return key

    @cached_property
    def _name(self) -> str | None:
        name = self.args.application
        while not name:
            name = input("Please enter the name of your application: ")
        return name

    @cached_property
    def _environment(self) -> str | None:
        environment = self.args.environment
        while not environment:
            environment = input(
                "Please enter the application environment (development/production): "
            )
        return environment
