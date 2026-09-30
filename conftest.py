from __future__ import annotations

import logging
import logging.config
import os
import platform
import tempfile
import threading
from collections.abc import Callable, Generator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from opentelemetry._logs import LogRecord, set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import (
    InMemoryLogRecordExporter,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import set_tracer_provider

from appsignal import probes
from appsignal.check_in.heartbeat import (
    _kill_continuous_heartbeats,
    _reset_heartbeat_continuous_interval_seconds,
)
from appsignal.check_in.scheduler import _reset_scheduler
from appsignal.client import _reset_client
from appsignal.heartbeat import _heartbeat_class_warning, _heartbeat_helper_warning
from appsignal.internal_logger import _reset_logger
from appsignal.opentelemetry import METRICS_PREFERRED_TEMPORALITY, _providers
from appsignal.tracing import _set_params_warning


class RecordingServer:
    def __init__(self) -> None:
        paths: list[str] = []
        self.paths = paths

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                self.rfile.read(int(self.headers.get("Content-Length", 0)))
                paths.append(self.path)
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *args: object) -> None:
                pass

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self._server.server_address[1]
        self.url = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()


@pytest.fixture
def recording_server() -> Generator[Callable[[], RecordingServer], None, None]:
    servers: list[RecordingServer] = []

    def start() -> RecordingServer:
        server = RecordingServer()
        servers.append(server)
        return server

    yield start

    for server in servers:
        server.close()


@pytest.fixture(scope="function", autouse=True)
def clear_proxy_variables(monkeypatch: Any) -> None:
    for name in ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"]:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(name.lower(), raising=False)


@pytest.fixture(scope="function", autouse=True)
def disable_start_opentelemetry(mocker: Any) -> Any:
    mocker.patch("appsignal.opentelemetry._start_tracer")
    mocker.patch("appsignal.opentelemetry._start_metrics")


@pytest.fixture(scope="function", autouse=True)
def reset_opentelemetry_providers() -> Any:
    yield

    _providers.clear()


@pytest.fixture(scope="session", autouse=True)
def start_in_memory_metric_reader() -> Generator[InMemoryMetricReader, None, None]:
    metric_reader = InMemoryMetricReader(
        preferred_temporality=METRICS_PREFERRED_TEMPORALITY
    )
    provider = MeterProvider(resource=Resource({}), metric_readers=[metric_reader])
    set_meter_provider(provider)

    yield metric_reader


@pytest.fixture(scope="session", autouse=True)
def start_in_memory_span_exporter() -> Generator[InMemorySpanExporter, None, None]:
    span_exporter = InMemorySpanExporter()
    exporter_processor = SimpleSpanProcessor(span_exporter)
    provider = TracerProvider()
    provider.add_span_processor(exporter_processor)
    set_tracer_provider(provider)

    yield span_exporter


@pytest.fixture(scope="function")
def metrics(
    start_in_memory_metric_reader: InMemoryMetricReader,
) -> Generator[Callable[[], Any], None, None]:
    # Getting the metrics data implicitly wipes its state
    start_in_memory_metric_reader.get_metrics_data()

    yield start_in_memory_metric_reader.get_metrics_data


@pytest.fixture(scope="function")
def spans(
    start_in_memory_span_exporter: InMemorySpanExporter,
) -> Generator[Callable[[], tuple[ReadableSpan, ...]], None, None]:
    start_in_memory_span_exporter.clear()

    def get_and_clear_spans() -> tuple[ReadableSpan, ...]:
        spans = start_in_memory_span_exporter.get_finished_spans()
        start_in_memory_span_exporter.clear()
        return spans

    yield get_and_clear_spans


@pytest.fixture(scope="session", autouse=True)
def start_in_memory_log_record_exporter() -> (
    Generator[InMemoryLogRecordExporter, None, None]
):
    log_record_exporter = InMemoryLogRecordExporter()
    provider = LoggerProvider()
    provider.add_log_record_processor(SimpleLogRecordProcessor(log_record_exporter))
    set_logger_provider(provider)

    yield log_record_exporter


@pytest.fixture(scope="function")
def log_records(
    start_in_memory_log_record_exporter: InMemoryLogRecordExporter,
) -> Generator[Callable[[], tuple[LogRecord, ...]], None, None]:
    start_in_memory_log_record_exporter.clear()

    def get_and_clear_log_records() -> tuple[LogRecord, ...]:
        log_records = tuple(
            log_record.log_record
            for log_record in start_in_memory_log_record_exporter.get_finished_logs()
        )
        start_in_memory_log_record_exporter.clear()
        return log_records

    yield get_and_clear_log_records


# Starting logging attaches a handler to the root logger, wraps the functions
# that configure the logging module, stops the internal loggers propagating
# and marks the instrumentation as installed. All of that lives on the logging
# module, so it outlives the test that started it and is put back here.
@pytest.fixture(scope="function", autouse=True)
def reset_logging_instrumentation() -> Any:
    configure_functions = (
        logging.basicConfig,
        logging.config.dictConfig,
        logging.config.fileConfig,
    )
    propagate = {
        name: logging.getLogger(name).propagate
        for name in ["appsignal", "opentelemetry"]
    }

    yield

    from opentelemetry.instrumentation.logging import LoggingInstrumentor

    instrumentor = LoggingInstrumentor()
    if instrumentor.is_instrumented_by_opentelemetry:
        instrumentor.uninstrument()

    (
        logging.basicConfig,
        logging.config.dictConfig,
        logging.config.fileConfig,
    ) = configure_functions

    for name, propagates in propagate.items():
        logging.getLogger(name).propagate = propagates

    from appsignal.opentelemetry import _warned_logger_names

    _warned_logger_names.clear()

    for name in ["duplicate", "duplicate_not_propagating", "duplicate_elsewhere"]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True


@pytest.fixture(scope="function", autouse=True)
def reset_environment_between_tests() -> Any:
    old_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(scope="function", autouse=True)
def reset_internal_logger_after_tests() -> Any:
    yield

    _reset_logger()


@pytest.fixture(scope="function", autouse=True)
def stop_and_clear_probes_after_tests() -> Any:
    yield

    probes.stop()
    probes.clear()


@pytest.fixture(scope="function", autouse=True)
def reset_global_client() -> Any:
    _reset_client()


@pytest.fixture(scope="function", autouse=True)
def reset_set_params_warning() -> Any:
    _set_params_warning.reset()


@pytest.fixture(scope="function", autouse=True)
def reset_checkins() -> Any:
    yield

    _reset_heartbeat_continuous_interval_seconds()
    _kill_continuous_heartbeats()
    _reset_scheduler()


@pytest.fixture(scope="function", autouse=True)
def stop_agent() -> Any:
    tmp_path = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    working_dir = os.path.join(tmp_path, "appsignal")
    if os.path.isdir(working_dir):
        os.system(f"rm -rf {working_dir}")


@pytest.fixture(scope="function")
def reset_heartbeat_warnings() -> Any:
    _heartbeat_class_warning.reset()
    _heartbeat_helper_warning.reset()

    yield
