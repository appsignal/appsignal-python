import os
import json

from appsignal.client import Client

from opentelemetry import trace

from .command import AppsignalCLICommand


class DemoCommand(AppsignalCLICommand):
    def __init__(self, push_api_key=None, application=None):
        self._push_api_key = push_api_key or os.environ.get("APPSIGNAL_PUSH_API_KEY")
        self._name = application or os.environ.get("APPSIGNAL_APP_NAME")

    def run(self) -> int:
        if self._push_api_key is None:
            self._input_push_api_key()

        if self._name is None:
            self._input_name()

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
