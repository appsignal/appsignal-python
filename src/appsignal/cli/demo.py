from __future__ import annotations

import json

from opentelemetry import trace

from ..client import Client
from .command import AppsignalCLICommand


class DemoCommand(AppsignalCLICommand):
    """Run demo application."""

    def run(self) -> int:
        print()

        client = Client(
            active=True,
            name=self._name,
            push_api_key=self._push_api_key,
            log_level="trace",
        )

        print("Sending example data to AppSignal...")
        print(f"Starting AppSignal client for {self._name}...")
        client.start()

        tracer = trace.get_tracer(__name__)

        # Performance sample
        with tracer.start_as_current_span("GET /demo") as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute(
                "appsignal.request.parameters",
                json.dumps({"GET": {"id": 1}, "POST": {}}),
            )
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
            span.set_attribute(
                "appsignal.request.parameters",
                json.dumps({"GET": {"id": 1}, "POST": {}}),
            )
            span.set_attribute(
                "demo_sample",
                True,
            )
            try:
                raise ValueError("Something went wrong")
            except ValueError as e:
                span.record_exception(e)

        return 0
