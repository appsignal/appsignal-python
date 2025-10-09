from __future__ import annotations

import os
import platform
import tempfile
from typing import Any, Callable, Generator

import pytest
from opentelemetry.metrics import set_meter_provider
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
from appsignal.opentelemetry import METRICS_PREFERRED_TEMPORALITY


@pytest.fixture(scope="function", autouse=True)
def disable_start_opentelemetry(mocker: Any) -> Any:
    mocker.patch("appsignal.opentelemetry._start_tracer")
    mocker.patch("appsignal.opentelemetry._start_metrics")


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
