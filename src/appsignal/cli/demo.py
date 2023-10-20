from __future__ import annotations

from argparse import ArgumentParser

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
        # Prompt for all the required config in a sensible order
        self._name  # noqa: B018
        self._environment  # noqa: B018
        self._push_api_key  # noqa: B018

        client = Client(
            active=True,
            environment=self._environment,
            name=self._name,
            push_api_key=self._push_api_key,
        )

        if not client._config.is_active():
            print("AppSignal not starting: no active config found.")
            return 1

        print("Sending example data to AppSignal...")
        print(f"Starting AppSignal client for {self._name}...")
        client.start()

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

        return 0
