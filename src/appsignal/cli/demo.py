from __future__ import annotations

from opentelemetry import trace

from ..client import Client
from ..tracing import set_params
from .command import AppsignalCLICommand


class DemoCommand(AppsignalCLICommand):
    """Run demo application."""

    def run(self) -> int:

        client = Client(
            active=True,
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
