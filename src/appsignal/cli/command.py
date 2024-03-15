from __future__ import annotations

import os
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass

from .. import _client_from_config_file
from ..client import Client
from ..config import Config, Options
from ..push_api_key_validator import PushApiKeyValidator
from .exit_error import ExitError


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

    def _push_api_key(self) -> str:
        key = self.args.push_api_key
        while not key:
            key = input("Please enter your Push API key: ")
        return key

    def _valid_push_api_key(self) -> str:
        while True:
            key = self._push_api_key()
            config = Config(Options(push_api_key=key))
            print("Validating API key...")
            print()

            try:
                validation_result = PushApiKeyValidator.validate(config)
            except Exception as e:
                print(f"Error while validating Push API key: {e}")
                print("Reach us at support@appsignal.com for support.")
                raise ExitError(1) from e

            if validation_result == "valid":
                print("✅ API key is valid!")
                return key

            if validation_result == "invalid":
                print(f"❌ API key {key} is not valid.")
                print("Please get a new one on https://appsignal.com and try again.")
                print()
                self.args.push_api_key = None
            else:
                print(
                    "Error while validating Push API key. HTTP status code: "
                    f"{validation_result}"
                )
                print("Reach us at support@appsignal.com for support.")
                raise ExitError(1)

    def _name(self) -> str:
        name = self.args.application
        while not name:
            name = input("Please enter the name of your application: ")
        return name

    def _environment(self) -> str:
        environment = self.args.environment
        while not environment:
            environment = input(
                "Please enter the application environment (development/production): "
            )
        return environment

    def _client_from_config_file(self) -> Client | None:
        try:
            return _client_from_config_file()
        except Exception as error:
            print(f"Error loading the __appsignal__.py configuration file:\n{error}\n")
            print("Exiting.")
            raise ExitError(1) from error
