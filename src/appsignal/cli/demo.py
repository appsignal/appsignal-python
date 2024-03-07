from __future__ import annotations

import time
from argparse import ArgumentParser

from opentelemetry import trace

from ..client import Client
from ..tracing import set_category, set_error, set_params, set_tag
from .command import AppsignalCLICommand


class DemoCommand(AppsignalCLICommand):
    """Send demonstration data to AppSignal."""

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        AppsignalCLICommand._application_argument(parser)
        AppsignalCLICommand._environment_argument(parser)
        AppsignalCLICommand._push_api_key_argument(parser)

    def run(self) -> int:
        client = self._client_from_config_file()

        if client:
            # For demo CLI purposes, AppSignal is always active
            client._config.options["active"] = True
            # Use CLI options if set
            app_name = self.args.application
            if app_name:
                client._config.options["name"] = app_name
            environment = self.args.environment
            if environment:
                client._config.options["environment"] = environment
            push_api_key = self.args.push_api_key
            if push_api_key:
                client._config.options["push_api_key"] = push_api_key
        else:
            name = self._name()
            environment = self._environment()
            push_api_key = self._push_api_key()
            client = Client(
                active=True,
                name=name,
                environment=environment,
                push_api_key=push_api_key,
            )

        if not client._config.is_active():
            print("AppSignal not starting: no active config found.")
            return 1

        app_name = client._config.option("name")
        print("Sending example data to AppSignal...")
        print(f"Starting AppSignal client for {app_name}...")
        client.start()

        Demo.transmit()

        return 0


class Demo:
    @staticmethod
    def transmit() -> None:
        tracer = trace.get_tracer(__name__)

        # Performance sample
        with tracer.start_as_current_span("GET /demo") as span:
            set_category("process_request.http")
            set_params({"GET": {"id": 1}, "POST": {}}, span)
            set_tag("demo_sample", True, span)
            time.sleep(0.1)

        # Error sample
        with tracer.start_as_current_span("GET /demo") as span:
            set_params({"GET": {"id": 1}, "POST": {}}, span)
            set_tag("demo_sample", True, span)
            try:
                raise DemoError("Something went wrong")
            except DemoError as e:
                set_error(e, span)


class DemoError(Exception):
    pass
