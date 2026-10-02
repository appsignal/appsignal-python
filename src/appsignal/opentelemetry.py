from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any, cast

import requests
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
from ._headers import normalize_headers
from .config import Config, list_to_env_str


if TYPE_CHECKING:
    import logging

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


def add_django_instrumentation(config: Config) -> None:
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse
    from opentelemetry.instrumentation.django import DjangoInstrumentor

    from .tracing import set_params, set_request_payload, set_request_query_parameters

    def response_hook(span: Span, request: HttpRequest, response: HttpResponse) -> None:
        if config.should_use_collector():
            set_request_query_parameters(request.GET, span)
            set_request_payload(request.POST, span)
        else:
            set_params({"GET": request.GET, "POST": request.POST}, span)

    DjangoInstrumentor().instrument(response_hook=response_hook)


def add_flask_instrumentation(_config: Config) -> None:
    from urllib.parse import parse_qs

    from opentelemetry.instrumentation.flask import FlaskInstrumentor

    from .tracing import set_request_query_parameters

    def request_hook(span: Span, environ: dict[str, str]) -> None:
        if span and span.is_recording():
            query_params = parse_qs(environ.get("QUERY_STRING", ""))
            set_request_query_parameters(query_params, span)

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

    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    instrumentor = LoggingInstrumentor()

    # The handler is attached to the root logger once per process, however
    # many times AppSignal is started in it.
    if instrumentor.is_instrumented_by_opentelemetry:
        return

    instrumentor.instrument(
        log_code_attributes=True,
        enable_log_auto_instrumentation=True,
    )

    _warn_about_logging_handlers()


# The OpenTelemetry log handler classes an application can attach itself. The
# one in the SDK is deprecated and is removed in a future release, so it is
# only looked for when it is there.
def _logging_handler_classes() -> tuple[tuple[type, ...], type | None]:
    from opentelemetry.instrumentation.logging.handler import LoggingHandler

    classes: list[type] = [LoggingHandler]
    deprecated: type | None = None

    try:
        from opentelemetry.sdk._logs import LoggingHandler as SDKLoggingHandler
    except ImportError:
        pass
    else:
        deprecated = SDKLoggingHandler
        classes.append(SDKLoggingHandler)

    return tuple(classes), deprecated


# What has already been warned about, as logger name and reason, so that an
# application that configures logging repeatedly is warned once for each.
_warned_logger_names: set[tuple[str, str]] = set()


def _warn_once(name: str, reason: str, message: str) -> None:
    if (name, reason) in _warned_logger_names:
        return

    _warned_logger_names.add((name, reason))
    logger.warning(message)


# Warn about the log handlers an application attached itself that send to the
# logger provider started here. A handler sending anywhere else belongs to
# another pipeline and is left alone.
#
# Our documentation used to advise attaching the handler in
# `opentelemetry.sdk._logs`, which is deprecated, and attaching a handler of
# your own, which duplicates the one attached here when the records it handles
# reach the root logger.
def _warn_about_logging_handlers() -> None:
    import logging

    from opentelemetry._logs import get_logger_provider
    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    ours = LoggingInstrumentor()._logging_handler
    provider = get_logger_provider()
    classes, deprecated = _logging_handler_classes()

    root = logging.getLogger()
    loggers = [root] + [
        configured
        for configured in root.manager.loggerDict.values()
        if isinstance(configured, logging.Logger)
    ]

    for configured in loggers:
        for handler in configured.handlers:
            if handler is ours or not isinstance(handler, classes):
                continue
            if getattr(handler, "_logger_provider", None) is not provider:
                continue

            name = configured.name if configured is not root else "the root logger"

            if deprecated is not None and isinstance(handler, deprecated):
                _warn_once(
                    name,
                    "deprecated",
                    f"The OpenTelemetry log handler attached to {name} is"
                    " imported from 'opentelemetry.sdk._logs', which is"
                    " deprecated and is removed in a future release. Import it"
                    " from 'opentelemetry.instrumentation.logging.handler'"
                    " instead, and construct it as"
                    " 'LoggingHandler(level=logging.NOTSET,"
                    " log_code_attributes=True)' to keep reporting the file,"
                    " function and line each log line came from.",
                )

            if ours is not None and _propagates_to_root(configured):
                _warn_once(
                    name,
                    "duplicate",
                    f"An OpenTelemetry log handler is attached to {name}. It"
                    " is redundant with the handler that AppSignal"
                    " automatically attaches to the root logger, and it will"
                    " cause every log line through it to be sent twice. Remove"
                    " it, or set the 'disable_default_instrumentations'"
                    " configuration option to ['logging'] to attach the log"
                    " handlers yourself.",
                )


# Whether the records this logger handles reach the root logger.
def _propagates_to_root(configured: logging.Logger) -> bool:
    import logging

    root = logging.getLogger()

    while configured is not root:
        if not configured.propagate:
            return False
        configured = configured.parent or root

    return True


# Warn again whenever the application configures the logging module, because
# that is when it attaches its own handlers. A handler attached any other way
# after this point is not seen.
def _warn_about_logging_handlers_on_reconfiguration() -> None:
    import logging.config

    def wrap(configure: Callable[..., None]) -> Callable[..., None]:
        def configure_and_warn(*args: Any, **kwargs: Any) -> None:
            configure(*args, **kwargs)
            _warn_about_logging_handlers()

        return configure_and_warn

    logging.config.dictConfig = wrap(logging.config.dictConfig)
    logging.config.fileConfig = wrap(logging.config.fileConfig)
    logging.basicConfig = wrap(logging.basicConfig)


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


Provider = TracerProvider | MeterProvider | LoggerProvider

# The providers started by this module. We keep our own references rather than
# reading the global providers back when stopping: no logger provider is set
# when the agent is used, an unset tracer provider is a proxy object with no
# `shutdown` method, and a provider the application set before ours is not ours
# to shut down.
_providers: list[Provider] = []


# The HTTP instrumentation reports a header only when it is named in one of
# these environment variables.
CAPTURE_HEADERS_ENVIRONMENT_VARIABLES: Mapping[str, str] = {
    "request_headers": "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST",
    "response_headers": "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE",
}


def _set_capture_headers(config: Config) -> None:
    for option, variable in CAPTURE_HEADERS_ENVIRONMENT_VARIABLES.items():
        headers = list_to_env_str(normalize_headers(config.option(option)))
        if headers:
            os.environ[variable] = headers


def start(config: Config) -> None:
    _set_capture_headers(config)

    _start_tracer(config)
    _start_metrics(config)

    # Configure OpenTelemetry logging only if a collector is used
    # (it is not currently supported by the agent)
    if config.should_instrument_logging():
        _start_logging(config)

    add_instrumentations(config)


def stop() -> None:
    # Shutting a provider down flushes what it has buffered. Each provider
    # unregisters its own `atexit` handler as part of shutting down, so this
    # does not cause them to be shut down twice.
    for provider in _providers:
        try:
            provider.shutdown()
        except Exception as error:
            name = type(provider).__name__
            logger.error(f"Failed to shut down the OpenTelemetry {name}: {error}")

    _providers.clear()


# Build the session an exporter sends its requests through, so that the proxy
# applies to the data sent to a collector. Returns `None` when there is no
# proxy, which leaves the exporter to build its own session. The agent listens
# on `localhost`, which a proxy on another host cannot reach, and is given the
# proxy to send its own data.
#
# A `requests` session that reads the environment lets the proxy variables
# override its own proxies, so it must not read them.
#
# Each exporter needs its own session, because they each send from their own
# thread and a `requests` session is not thread safe.
def _exporter_session(config: Config) -> requests.Session | None:
    if not config.should_use_external_collector():
        return None

    proxy = config.proxy_for(_opentelemetry_endpoint(config))

    if not proxy:
        return None

    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": proxy, "https": proxy}
    return session


def _otlp_span_processor(config: Config) -> BatchSpanProcessor:
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{_opentelemetry_endpoint(config)}/v1/traces",
        certificate_file=config.option("ca_file_path"),
        session=_exporter_session(config),
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
    _providers.append(provider)


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
        certificate_file=config.option("ca_file_path"),
        session=_exporter_session(config),
        preferred_temporality=METRICS_PREFERRED_TEMPORALITY,
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=10000
    )

    provider = MeterProvider(resource=_resource(config), metric_readers=[metric_reader])
    metrics.set_meter_provider(provider)
    _providers.append(provider)


def _start_logging(config: Config) -> None:
    log_exporter = OTLPLogExporter(
        endpoint=f"{_opentelemetry_endpoint(config)}/v1/logs",
        certificate_file=config.option("ca_file_path"),
        session=_exporter_session(config),
    )
    provider = LoggerProvider(resource=_resource(config))
    provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    logs.set_logger_provider(provider)
    _providers.append(provider)

    _silence_internal_loggers()
    _warn_about_logging_handlers()
    _warn_about_logging_handlers_on_reconfiguration()


# Keep the log lines AppSignal and the OpenTelemetry SDK write about
# themselves out of the logs sent to AppSignal. A log handler sending to the
# logger provider started here receives everything that reaches the root
# logger, whether the handler was attached here or by the application.
def _silence_internal_loggers() -> None:
    import logging

    for name in ["appsignal", "opentelemetry"]:
        logging.getLogger(name).propagate = False


def _resource(config: Config) -> Resource:
    # Ask for the resource detector that reports the process, so that the
    # process id is reported alongside the instance id. Naming the detector in
    # this variable is what makes each provider run it again when it refreshes
    # the resource after a fork.
    os.environ["OTEL_EXPERIMENTAL_RESOURCE_DETECTORS"] = "process"

    attributes = {
        key: value
        for key, value in {
            "appsignal.config.name": config.options.get("name"),
            "appsignal.config.environment": config.options.get("environment"),
            "appsignal.config.push_api_key": config.options.get("push_api_key"),
            "appsignal.config.revision": config.options.get("revision") or "unknown",
            "appsignal.config.app_path": config.options.get("app_path"),
            "appsignal.config.platform": config.options.get("platform"),
            "appsignal.config.language_integration": "python",
            "service.name": config.options.get("service_name") or "app",
            "host.name": config.options.get("hostname") or "unknown",
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
            "appsignal.config.ignore_logs": config.options.get("ignore_logs"),
            "appsignal.config.ignore_namespaces": config.options.get(
                "ignore_namespaces"
            ),
            "appsignal.config.response_headers": normalize_headers(
                config.options.get("response_headers")
            ),
            "appsignal.config.request_headers": normalize_headers(
                config.options.get("request_headers")
            ),
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

    # `Resource.create` runs the resource detectors, one of which gives the
    # process a `service.instance.id`. Each provider re-runs them after a fork,
    # so a forked worker reports under an identity of its own. The attributes
    # passed here win over what a detector or `OTEL_RESOURCE_ATTRIBUTES`
    # provides.
    return Resource.create(cast(Mapping[str, str | list[str]], attributes))


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
