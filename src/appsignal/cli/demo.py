from __future__ import annotations

import os
from argparse import ArgumentParser
from runpy import run_path

from opentelemetry import trace

from ..client import Client
from ..tracing import set_params
from .command import AppsignalCLICommand


class DemoCommand(AppsignalCLICommand):
    """Run demo application."""

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        AppsignalCLICommand._application_argument(parser)
        AppsignalCLICommand._environment_argument(parser)
        AppsignalCLICommand._push_api_key_argument(parser)

    def run(self) -> int:
        cwd = os.getcwd()
        app_config_path = os.path.join(cwd, "__appsignal__.py")
        if os.path.exists(app_config_path):
            try:
                client = run_path(app_config_path)["appsignal"]
            except KeyError:
                print(
                    "No `appsignal` variable exported by the __appsignal__.py "
                    "config file."
                    "Please update the __appsignal__.py file as described in "
                    "our documentation: "
                    "https://docs.appsignal.com/python/configuration.html "
                    "Exiting."
                )
                return 1

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
            # Prompt for all the required config in a sensible order
            self._name  # noqa: B018
            self._environment  # noqa: B018
            self._push_api_key  # noqa: B018
            client = Client(
                active=True,
                name=self._name,
                environment=self._environment,
                push_api_key=self._push_api_key,
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
            span.set_attribute("http.method", "GET")
            set_params({"GET": {"id": 1}, "POST": {}}, span)
            span.set_attribute(
                "otel.instrumentation_library.name",
                "opentelemetry.instrumentation.wsgi",
            )
            span.set_attribute(
                "demo_sample",
                True,
            )

        # Error sample
        with tracer.start_as_current_span("GET /demo") as span:
            span.set_attribute("http.method", "GET")
            set_params({"GET": {"id": 1}, "POST": {}}, span)
            span.set_attribute(
                "demo_sample",
                True,
            )
            try:
                raise ValueError("Something went wrong")
            except ValueError as e:
                span.record_exception(e)
