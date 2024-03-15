from __future__ import annotations

import logging
import os
import platform
import tempfile

import pytest
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import set_tracer_provider

from appsignal.agent import agent
from appsignal.opentelemetry import METRICS_PREFERRED_TEMPORALITY


@pytest.fixture(scope="function", autouse=True)
def disable_start_opentelemetry(mocker):
    mocker.patch("appsignal.opentelemetry._start_tracer")
    mocker.patch("appsignal.opentelemetry._start_metrics")


@pytest.fixture(scope="session", autouse=True)
def start_in_memory_metric_reader():
    metric_reader = InMemoryMetricReader(
        preferred_temporality=METRICS_PREFERRED_TEMPORALITY
    )
    provider = MeterProvider(resource=Resource({}), metric_readers=[metric_reader])
    set_meter_provider(provider)

    yield metric_reader


@pytest.fixture(scope="session", autouse=True)
def start_in_memory_span_exporter():
    span_exporter = InMemorySpanExporter()
    exporter_processor = SimpleSpanProcessor(span_exporter)
    provider = TracerProvider()
    provider.add_span_processor(exporter_processor)
    set_tracer_provider(provider)

    yield span_exporter


@pytest.fixture(scope="function")
def metrics(start_in_memory_metric_reader):
    # Getting the metrics data implicitly wipes its state
    start_in_memory_metric_reader.get_metrics_data()

    yield start_in_memory_metric_reader.get_metrics_data


@pytest.fixture(scope="function")
def spans(start_in_memory_span_exporter):
    start_in_memory_span_exporter.clear()

    def get_and_clear_spans():
        spans = start_in_memory_span_exporter.get_finished_spans()
        start_in_memory_span_exporter.clear()
        return spans

    yield get_and_clear_spans


@pytest.fixture(scope="function", autouse=True)
def reset_environment_between_tests():
    old_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(scope="function", autouse=True)
def remove_logging_handlers_after_tests():
    yield

    logger = logging.getLogger("appsignal")
    for handler in logger.handlers:
        logger.removeHandler(handler)


@pytest.fixture(scope="function", autouse=True)
def remove_probes_after_tests():
    yield

    from appsignal.probes import _probes, _probe_states

    _probes.clear()
    _probe_states.clear()


@pytest.fixture(scope="function", autouse=True)
def reset_agent_active_state():
    agent.active = False


@pytest.fixture(scope="function", autouse=True)
def stop_agent():
    tmp_path = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    working_dir = os.path.join(tmp_path, "appsignal")
    if os.path.isdir(working_dir):
        os.system(f"rm -rf {working_dir}")
