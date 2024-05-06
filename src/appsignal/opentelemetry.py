from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, Mapping

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    MeterProvider,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ConcurrentMultiSpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from . import internal_logger as logger
from .config import Config, list_to_env_str


if TYPE_CHECKING:
    from opentelemetry.trace.span import Span


def add_aiopg_instrumentation() -> None:
    from opentelemetry.instrumentation.aiopg import AiopgInstrumentor

    AiopgInstrumentor().instrument()


def add_asyncpg_instrumentation() -> None:
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

    AsyncPGInstrumentor().instrument()


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


def add_mysql_instrumentation() -> None:
    from opentelemetry.instrumentation.mysql import MySQLInstrumentor

    MySQLInstrumentor().instrument()


def add_mysqlclient_instrumentation() -> None:
    from opentelemetry.instrumentation.mysqlclient import MySQLClientInstrumentor

    MySQLClientInstrumentor().instrument()


def add_psycopg2_instrumentation() -> None:
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

    Psycopg2Instrumentor().instrument()


def add_psycopg_instrumentation() -> None:
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor

    PsycopgInstrumentor().instrument()


def add_pymysql_instrumentation() -> None:
    from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor

    PyMySQLInstrumentor().instrument()


def add_redis_instrumentation() -> None:
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument(sanitize_query=True)


def add_requests_instrumentation() -> None:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    RequestsInstrumentor().instrument()


def add_sqlalchemy_instrumentation() -> None:
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument()


def add_sqlite3_instrumentation() -> None:
    from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

    SQLite3Instrumentor().instrument()


DefaultInstrumentationAdder = Callable[[], None]

DEFAULT_INSTRUMENTATION_ADDERS: Mapping[
    Config.DefaultInstrumentation, DefaultInstrumentationAdder
] = {
    "opentelemetry.instrumentation.aiopg": add_aiopg_instrumentation,
    "opentelemetry.instrumentation.asyncpg": add_asyncpg_instrumentation,
    "opentelemetry.instrumentation.celery": add_celery_instrumentation,
    "opentelemetry.instrumentation.django": add_django_instrumentation,
    "opentelemetry.instrumentation.flask": add_flask_instrumentation,
    "opentelemetry.instrumentation.jinja2": add_jinja2_instrumentation,
    "opentelemetry.instrumentation.mysql": add_mysql_instrumentation,
    "opentelemetry.instrumentation.mysqlclient": add_mysqlclient_instrumentation,
    "opentelemetry.instrumentation.psycopg2": add_psycopg2_instrumentation,
    "opentelemetry.instrumentation.psycopg": add_psycopg_instrumentation,
    "opentelemetry.instrumentation.pymysql": add_pymysql_instrumentation,
    "opentelemetry.instrumentation.redis": add_redis_instrumentation,
    "opentelemetry.instrumentation.requests": add_requests_instrumentation,
    "opentelemetry.instrumentation.sqlalchemy": add_sqlalchemy_instrumentation,
    "opentelemetry.instrumentation.sqlite3": add_sqlite3_instrumentation,
}


def start(config: Config) -> None:
    # Configure OpenTelemetry request headers config
    request_headers = list_to_env_str(config.option("request_headers"))
    if request_headers:
        os.environ["OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"] = (
            request_headers
        )

    opentelemetry_port = config.option("opentelemetry_port")
    _start_tracer(opentelemetry_port, config.option("log_level") == "trace")
    _start_metrics(opentelemetry_port)

    add_instrumentations(config)


def _otlp_span_processor(opentelemetry_port: str | int) -> BatchSpanProcessor:
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://localhost:{opentelemetry_port}/v1/traces"
    )
    return BatchSpanProcessor(otlp_exporter)


def _console_span_processor() -> SimpleSpanProcessor:
    console_exporter = ConsoleSpanExporter()
    return SimpleSpanProcessor(console_exporter)


def _start_tracer(opentelemetry_port: str | int, should_trace: bool = False) -> None:
    otlp_span_processor = _otlp_span_processor(opentelemetry_port)
    provider = TracerProvider()

    if should_trace:
        multi_span_processor = ConcurrentMultiSpanProcessor()
        multi_span_processor.add_span_processor(otlp_span_processor)
        multi_span_processor.add_span_processor(_console_span_processor())
        provider.add_span_processor(multi_span_processor)
    else:
        provider.add_span_processor(otlp_span_processor)

    trace.set_tracer_provider(provider)


METRICS_PREFERRED_TEMPORALITY: dict[type, AggregationTemporality] = {
    Counter: AggregationTemporality.DELTA,
    UpDownCounter: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
    ObservableUpDownCounter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
}


def _start_metrics(opentelemetry_port: str | int) -> None:
    metric_exporter = OTLPMetricExporter(
        endpoint=f"http://localhost:{opentelemetry_port}/v1/metrics",
        preferred_temporality=METRICS_PREFERRED_TEMPORALITY,
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=10000
    )

    resource = Resource(attributes={"appsignal.service.process_id": os.getpid()})
    provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)


def add_instrumentations(
    config: Config,
    _adders: Mapping[
        Config.DefaultInstrumentation, DefaultInstrumentationAdder
    ] = DEFAULT_INSTRUMENTATION_ADDERS,
) -> None:
    disable_list = config.options.get("disable_default_instrumentations") or []

    if disable_list is True:
        return

    for name, adder in _adders.items():
        if name not in disable_list:
            try:
                adder()
                logger.info(f"Instrumented {name}")
            except ModuleNotFoundError:
                pass
