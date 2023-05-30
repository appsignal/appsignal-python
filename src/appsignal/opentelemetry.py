from __future__ import annotations
import os
from typing import Dict
import logging

from .config import Config, list_to_env_str

from typing import Callable

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def add_celery_instrumentation():
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()


def add_django_instrumentation():
    from opentelemetry.instrumentation.django import DjangoInstrumentor
    import json

    def response_hook(span, request, response):
        span.set_attribute(
            "appsignal.request.parameters",
            json.dumps({"GET": request.GET, "POST": request.POST}),
        )

    DjangoInstrumentor().instrument(response_hook=response_hook)


def add_flask_instrumentation():
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    import json
    from urllib.parse import parse_qs

    def request_hook(span, environ):
        if span and span.is_recording():
            query_params = parse_qs(environ.get("QUERY_STRING", ""))
            span.set_attribute(
                "appsignal.request.parameters", json.dumps({"args": query_params})
            )

    FlaskInstrumentor().instrument(request_hook=request_hook)


def add_jinja2_instrumentation():
    from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor

    Jinja2Instrumentor().instrument()


def add_psycopg2_instrumentation():
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

    Psycopg2Instrumentor().instrument(enable_commenter=True, commenter_options={})


def add_redis_instrumentation():
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument(sanitize_query=True)


def add_requests_instrumentation():
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    RequestsInstrumentor().instrument()


DefaultInstrumentationAdder = Callable[[], None]
DefaultInstrumentationAdders = Dict[
    Config.DefaultInstrumentation, DefaultInstrumentationAdder
]

DEFAULT_INSTRUMENTATION_ADDERS: DefaultInstrumentationAdders = {
    "opentelemetry.instrumentation.celery": add_celery_instrumentation,
    "opentelemetry.instrumentation.django": add_django_instrumentation,
    "opentelemetry.instrumentation.flask": add_flask_instrumentation,
    "opentelemetry.instrumentation.jinja2": add_jinja2_instrumentation,
    "opentelemetry.instrumentation.psycopg2": add_psycopg2_instrumentation,
    "opentelemetry.instrumentation.redis": add_redis_instrumentation,
    "opentelemetry.instrumentation.requests": add_requests_instrumentation,
}


def start_opentelemetry(config: Config):
    # Configure OpenTelemetry request headers config
    request_headers = list_to_env_str(config.option("request_headers"))
    if request_headers:
        os.environ[
            "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"
        ] = request_headers

    provider = TracerProvider()

    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:8099")
    exporter_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(exporter_processor)
    trace.set_tracer_provider(provider)

    add_instrumentations(config)


def add_instrumentations(
    config: Config, default_instrumentation_adders=DEFAULT_INSTRUMENTATION_ADDERS
):
    logger = logging.getLogger("appsignal")
    disable_list = config.options.get("disable_default_instrumentations") or []

    if disable_list is True:
        return

    for name, adder in default_instrumentation_adders.items():
        if name not in disable_list:
            try:
                logger.info(f"Instrumenting {name}")
                adder()
            except ModuleNotFoundError:
                pass
