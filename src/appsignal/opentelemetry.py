from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, List, Mapping, Union, cast

from opentelemetry import _logs as logs
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
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


def add_aiopg_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.aiopg import AiopgInstrumentor

    AiopgInstrumentor().instrument()


def add_asyncpg_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

    AsyncPGInstrumentor().instrument()


def add_celery_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()


def add_django_instrumentation(_config: Config) -> None:
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


def add_flask_instrumentation(_config: Config) -> None:
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


def add_jinja2_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor

    Jinja2Instrumentor().instrument()


def add_mysql_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.mysql import MySQLInstrumentor

    MySQLInstrumentor().instrument()


def add_mysqlclient_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.mysqlclient import MySQLClientInstrumentor

    MySQLClientInstrumentor().instrument()


def add_pika_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.pika import PikaInstrumentor

    PikaInstrumentor().instrument()


def add_psycopg2_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

    Psycopg2Instrumentor().instrument()


def add_psycopg_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor

    PsycopgInstrumentor().instrument()


def add_pymysql_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor

    PyMySQLInstrumentor().instrument()


def add_redis_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument(sanitize_query=True)


def add_requests_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor

    RequestsInstrumentor().instrument()


def add_sqlalchemy_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument()


def add_sqlite3_instrumentation(_config: Config) -> None:
    from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

    SQLite3Instrumentor().instrument()


def add_logging_instrumentation(config: Config) -> None:
    # Do not add a root logging handler if we should not support
    # instrumenting logging.
    if not config.should_instrument_logging():
        return

    import logging

    from opentelemetry.sdk._logs import LoggingHandler

    # Attach OTel LoggingHandler to the root logger
    handler = LoggingHandler(level=logging.NOTSET)
    logger = logging.getLogger()
    logger.addHandler(handler)

    # Configure the OpenTelemetry loggers and the AppSignal internal
    # logger to not propagate to the root logger. This prevents
    # internal logs from being sent to AppSignal.
    opentelemetry_logger = logging.getLogger("opentelemetry")
    opentelemetry_logger.propagate = False
    appsignal_logger = logging.getLogger("appsignal")
    appsignal_logger.propagate = False


DefaultInstrumentationAdder = Callable[[Config], None]

DEFAULT_INSTRUMENTATION_ADDERS: Mapping[
    Config.DefaultInstrumentation, DefaultInstrumentationAdder
] = {
    "aiopg": add_aiopg_instrumentation,
    "asyncpg": add_asyncpg_instrumentation,
    "celery": add_celery_instrumentation,
    "django": add_django_instrumentation,
    "flask": add_flask_instrumentation,
    "jinja2": add_jinja2_instrumentation,
    "mysql": add_mysql_instrumentation,
    "mysqlclient": add_mysqlclient_instrumentation,
    "pika": add_pika_instrumentation,
    "psycopg2": add_psycopg2_instrumentation,
    "psycopg": add_psycopg_instrumentation,
    "pymysql": add_pymysql_instrumentation,
    "redis": add_redis_instrumentation,
    "requests": add_requests_instrumentation,
    "sqlalchemy": add_sqlalchemy_instrumentation,
    "sqlite3": add_sqlite3_instrumentation,
    "logging": add_logging_instrumentation,
}


def start(config: Config) -> None:
    # Configure OpenTelemetry request headers config
    request_headers = list_to_env_str(config.option("request_headers"))
    if request_headers:
        os.environ["OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"] = (
            request_headers
        )

    _start_tracer(config)
    _start_metrics(config)

    # Configure OpenTelemetry logging only if a collector is used
    # (it is not currently supported by the agent)
    if config.should_instrument_logging():
        _start_logging(config)

    add_instrumentations(config)


def _otlp_span_processor(config: Config) -> BatchSpanProcessor:
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{_opentelemetry_endpoint(config)}/v1/traces",
    )
    return BatchSpanProcessor(otlp_exporter)


def _console_span_processor() -> SimpleSpanProcessor:
    console_exporter = ConsoleSpanExporter()
    return SimpleSpanProcessor(console_exporter)


def _start_tracer(config: Config) -> None:
    otlp_span_processor = _otlp_span_processor(config)
    provider = TracerProvider(resource=_resource(config))

    should_trace = config.option("log_level") == "trace"

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


def _start_metrics(config: Config) -> None:
    metric_exporter = OTLPMetricExporter(
        endpoint=f"{_opentelemetry_endpoint(config)}/v1/metrics",
        preferred_temporality=METRICS_PREFERRED_TEMPORALITY,
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=10000
    )

    provider = MeterProvider(resource=_resource(config), metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)


def _start_logging(config: Config) -> None:
    log_exporter = OTLPLogExporter(
        endpoint=f"{_opentelemetry_endpoint(config)}/v1/logs",
    )
    provider = LoggerProvider(resource=_resource(config))
    provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    logs.set_logger_provider(provider)


def _resource(config: Config) -> Resource:
    attributes = {
        key: value
        for key, value in {
            "appsignal.config.name": config.options.get("name"),
            "appsignal.config.environment": config.options.get("environment"),
            "appsignal.config.push_api_key": config.options.get("push_api_key"),
            "appsignal.config.revision": config.options.get("revision", "unknown"),
            "appsignal.config.language_integration": "python",
            "service.name": config.options.get("service_name", "unknown"),
            "host.name": config.options.get("hostname", "unknown"),
            "appsignal.service.process_id": os.getpid(),
            "appsignal.config.filter_attributes": config.options.get(
                "filter_attributes"
            ),
            "appsignal.config.filter_function_parameters": config.options.get(
                "filter_function_parameters"
            ),
            "appsignal.config.filter_request_query_parameters": config.options.get(
                "filter_request_query_parameters"
            ),
            "appsignal.config.filter_request_payload": config.options.get(
                "filter_request_payload"
            ),
            "appsignal.config.filter_request_session_data": config.options.get(
                "filter_session_data"
            ),
            "appsignal.config.ignore_actions": config.options.get("ignore_actions"),
            "appsignal.config.ignore_errors": config.options.get("ignore_errors"),
            "appsignal.config.ignore_namespaces": config.options.get(
                "ignore_namespaces"
            ),
            "appsignal.config.response_headers": config.options.get("response_headers"),
            "appsignal.config.request_headers": config.options.get("request_headers"),
            "appsignal.config.send_function_parameters": config.options.get(
                "send_function_parameters"
            ),
            "appsignal.config.send_request_query_parameters": config.options.get(
                "send_request_query_parameters"
            ),
            "appsignal.config.send_request_payload": config.options.get(
                "send_request_payload"
            ),
            "appsignal.config.send_request_session_data": config.options.get(
                "send_session_data"
            ),
        }.items()
        if value is not None
    }

    return Resource(attributes=cast(Mapping[str, Union[str, List[str]]], attributes))


def _opentelemetry_endpoint(config: Config) -> str:
    collector_endpoint = config.options.get("collector_endpoint")
    if collector_endpoint:
        # Remove trailing slashes (it will be concatenated
        # with /v1/{traces,metrics,logs} later)
        return collector_endpoint.rstrip("/")

    opentelemetry_port = config.option("opentelemetry_port")
    return f"http://localhost:{opentelemetry_port}"


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
        if (
            name not in disable_list
            and f"opentelemetry.instrumentation.{name}" not in disable_list
        ):
            try:
                adder(config)
                logger.info(f"Instrumented {name}")
            except ModuleNotFoundError:
                pass
