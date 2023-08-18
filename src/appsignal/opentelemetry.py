from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Callable, Mapping

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import Config, list_to_env_str


if TYPE_CHECKING:
    from opentelemetry.trace.span import Span


def add_celery_instrumentation() -> None:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()


def add_django_instrumentation() -> None:
    import json

    from django.http.request import HttpRequest
    from django.http.response import HttpResponse
    from opentelemetry.instrumentation.django import DjangoInstrumentor

    def response_hook(span: Span, request: HttpRequest, response: HttpResponse) -> None:
        span.set_attribute(
            "appsignal.request.parameters",
            json.dumps({"GET": request.GET, "POST": request.POST}),
        )

    DjangoInstrumentor().instrument(response_hook=response_hook)


def add_flask_instrumentation() -> None:
    import json
    from urllib.parse import parse_qs

    from opentelemetry.instrumentation.flask import FlaskInstrumentor

    def request_hook(span: Span, environ: dict[str, str]) -> None:
        if span and span.is_recording():
            query_params = parse_qs(environ.get("QUERY_STRING", ""))
            span.set_attribute(
                "appsignal.request.parameters", json.dumps({"args": query_params})
            )

    FlaskInstrumentor().instrument(request_hook=request_hook)


def add_jinja2_instrumentation() -> None:
    from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor

    Jinja2Instrumentor().instrument()


def add_psycopg2_instrumentation() -> None:
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

    Psycopg2Instrumentor().instrument(enable_commenter=True, commenter_options={})


def add_redis_instrumentation() -> None:
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument(sanitize_query=True)


def add_requests_instrumentation() -> None:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    RequestsInstrumentor().instrument()


DefaultInstrumentationAdder = Callable[[], None]

DEFAULT_INSTRUMENTATION_ADDERS: Mapping[
    Config.DefaultInstrumentation, DefaultInstrumentationAdder
] = {
    "opentelemetry.instrumentation.celery": add_celery_instrumentation,
    "opentelemetry.instrumentation.django": add_django_instrumentation,
    "opentelemetry.instrumentation.flask": add_flask_instrumentation,
    "opentelemetry.instrumentation.jinja2": add_jinja2_instrumentation,
    "opentelemetry.instrumentation.psycopg2": add_psycopg2_instrumentation,
    "opentelemetry.instrumentation.redis": add_redis_instrumentation,
    "opentelemetry.instrumentation.requests": add_requests_instrumentation,
}


def start_opentelemetry(config: Config) -> None:
    # Configure OpenTelemetry request headers config
    request_headers = list_to_env_str(config.option("request_headers"))
    if request_headers:
        os.environ[
            "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"
        ] = request_headers

    provider = TracerProvider()

    opentelemetry_port = config.option("opentelemetry_port")
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://localhost:{opentelemetry_port}/v1/traces"
    )
    exporter_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(exporter_processor)
    trace.set_tracer_provider(provider)

    add_instrumentations(config)


def add_instrumentations(
    config: Config,
    _adders: Mapping[
        Config.DefaultInstrumentation, DefaultInstrumentationAdder
    ] = DEFAULT_INSTRUMENTATION_ADDERS,
) -> None:
    logger = logging.getLogger("appsignal")
    disable_list = config.options.get("disable_default_instrumentations") or []

    if disable_list is True:
        return

    for name, adder in _adders.items():
        if name not in disable_list:
            try:
                logger.info(f"Instrumenting {name}")
                adder()
            except ModuleNotFoundError:
                pass
