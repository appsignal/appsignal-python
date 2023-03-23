from __future__ import annotations

from .config import Options, opentelemetry_resource_attributes, DEFAULT_INSTRUMENTATION

from typing import Callable

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
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


DEFAULT_INSTRUMENTATION_ADDERS: dict[DEFAULT_INSTRUMENTATION, Callable[[], None]] = {
    "opentelemetry.instrumentation.celery": add_celery_instrumentation,
    "opentelemetry.instrumentation.django": add_django_instrumentation,
    "opentelemetry.instrumentation.jinja2": add_jinja2_instrumentation,
    "opentelemetry.instrumentation.psycopg2": add_psycopg2_instrumentation,
    "opentelemetry.instrumentation.redis": add_redis_instrumentation,
    "opentelemetry.instrumentation.requests": add_requests_instrumentation,
}


def start_opentelemetry(config: Options):
    resource = Resource(attributes=opentelemetry_resource_attributes(config))
    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:8099")
    exporter_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(exporter_processor)
    trace.set_tracer_provider(provider)

    add_instrumentations(config)


def add_instrumentations(config: Options):
    disable_list = config.get("disable_default_instrumentations") or []

    if disable_list is True:
        return

    for name, adder in DEFAULT_INSTRUMENTATION_ADDERS.items():
        if name not in disable_list:
            try:
                adder()
            except ModuleNotFoundError:
                pass
