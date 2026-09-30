from __future__ import annotations

import logging
import logging.config
import os
from typing import cast
from unittest.mock import Mock

from opentelemetry.instrumentation.logging.handler import LoggingHandler
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler as SDKLoggingHandler
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from appsignal.config import Config, Options
from appsignal.opentelemetry import (
    _exporter_session,
    _otlp_span_processor,
    _providers,
    _resource,
    _set_capture_headers,
    _start_logging,
    _start_metrics,
    _start_tracer,
    add_instrumentations,
    add_logging_instrumentation,
    stop,
)


REQUEST_HEADERS_VARIABLE = "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST"
RESPONSE_HEADERS_VARIABLE = "OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE"


def export_a_span(config: Config, mocker) -> None:
    mocker.patch("appsignal.opentelemetry.BatchSpanProcessor", SimpleSpanProcessor)
    provider = TracerProvider()
    provider.add_span_processor(_otlp_span_processor(config))
    provider.get_tracer(__name__).start_span("span").end()
    provider.shutdown()


def test_set_capture_headers():
    config = Config(
        Options(
            request_headers=["accept", "x-request-id"],
            response_headers=["content-type"],
        )
    )

    _set_capture_headers(config)

    assert os.environ[REQUEST_HEADERS_VARIABLE] == "accept,x-request-id"
    assert os.environ[RESPONSE_HEADERS_VARIABLE] == "content-type"


def test_set_capture_headers_normalizes_the_names():
    config = Config(
        Options(
            request_headers=["Accept_Charset", "X-Custom-Header"],
            response_headers=["Content_Type"],
        )
    )

    _set_capture_headers(config)

    assert os.environ[REQUEST_HEADERS_VARIABLE] == "accept-charset,x-custom-header"
    assert os.environ[RESPONSE_HEADERS_VARIABLE] == "content-type"


def test_set_capture_headers_when_the_options_are_empty():
    config = Config(Options(request_headers=[], response_headers=[]))

    _set_capture_headers(config)

    assert REQUEST_HEADERS_VARIABLE not in os.environ
    assert RESPONSE_HEADERS_VARIABLE not in os.environ


def test_set_capture_headers_when_the_options_are_unset():
    config = Config(Options(request_headers=None))

    _set_capture_headers(config)

    assert REQUEST_HEADERS_VARIABLE not in os.environ
    assert RESPONSE_HEADERS_VARIABLE not in os.environ


def test_resource_normalizes_the_header_options():
    config = Config(
        Options(
            name="MyApp",
            push_api_key="0000-0000-0000-0000",
            request_headers=["Accept_Charset"],
            response_headers=["Content_Type"],
        )
    )

    attributes = _resource(config).attributes

    assert attributes["appsignal.config.request_headers"] == ("accept-charset",)
    assert attributes["appsignal.config.response_headers"] == ("content-type",)


def raise_module_not_found_error(_config: Config) -> None:
    raise ModuleNotFoundError


def mock_adders() -> dict[Config.DefaultInstrumentation, Mock]:
    return {
        "celery": Mock(),
        "jinja2": Mock(side_effect=raise_module_not_found_error),
    }


def test_add_instrumentations():
    adders = mock_adders()
    config = Config()

    add_instrumentations(config, _adders=adders)

    for adder in adders.values():
        adder.assert_called_once()


def test_add_instrumentations_disable_some_default_instrumentations():
    adders = mock_adders()
    config = Config(Options(disable_default_instrumentations=["celery"]))

    add_instrumentations(config, _adders=adders)

    adders["celery"].assert_not_called()
    adders["jinja2"].assert_called_once()


def test_disable_default_instrumentations_backwards_compatibility_prefix():
    adders = mock_adders()
    config = Config(
        Options(
            disable_default_instrumentations=cast(
                list[Config.DefaultInstrumentation],
                ["opentelemetry.instrumentation.celery"],
            )
        )
    )

    add_instrumentations(config, _adders=adders)

    adders["celery"].assert_not_called()
    adders["jinja2"].assert_called_once()


def test_add_instrumentations_disable_all_default_instrumentations():
    adders = mock_adders()
    config = Config(Options(disable_default_instrumentations=True))

    add_instrumentations(config, _adders=adders)

    for adder in adders.values():
        adder.assert_not_called()


def logging_handlers():
    return [
        handler
        for handler in logging.getLogger().handlers
        if isinstance(handler, LoggingHandler)
    ]


def test_add_logging_instrumentation():
    config = Config(Options(collector_endpoint="https://collector.example"))

    add_logging_instrumentation(config)

    assert len(logging_handlers()) == 1


def test_start_logging_silences_the_internal_loggers():
    _start_logging(Config(COLLECTOR_OPTIONS))

    assert not logging.getLogger("appsignal").propagate
    assert not logging.getLogger("opentelemetry").propagate


# An application that attaches the log handler itself disables the logging
# instrumentation, and a handler it attaches to the root logger receives
# whatever reaches it, including what AppSignal logs about itself.
def test_start_logging_silences_them_without_the_instrumentation():
    config = Config(
        Options(
            collector_endpoint="https://collector.example",
            disable_default_instrumentations=["logging"],
        )
    )

    _start_logging(config)
    add_instrumentations(config)

    assert logging_handlers() == []
    assert not logging.getLogger("appsignal").propagate
    assert not logging.getLogger("opentelemetry").propagate


def test_add_logging_instrumentation_only_attaches_one_handler():
    config = Config(Options(collector_endpoint="https://collector.example"))

    add_logging_instrumentation(config)
    add_logging_instrumentation(config)

    assert len(logging_handlers()) == 1


def test_add_logging_instrumentation_without_a_collector():
    config = Config()

    add_logging_instrumentation(config)

    assert logging_handlers() == []


def test_add_logging_instrumentation_reports_the_code_and_exception(log_records):
    config = Config(Options(collector_endpoint="https://collector.example"))
    add_logging_instrumentation(config)

    logger = logging.getLogger("test_add_logging_instrumentation")
    logger.setLevel(logging.ERROR)
    try:
        raise ValueError("An exception")
    except ValueError:
        logger.exception("Something went wrong")

    (log_record,) = log_records()

    assert log_record.body == "Something went wrong"
    assert log_record.severity_text == "ERROR"
    assert log_record.attributes["code.function.name"] == (
        "test_add_logging_instrumentation_reports_the_code_and_exception"
    )
    assert log_record.attributes["code.file.path"] == __file__
    assert log_record.attributes["exception.type"] == "ValueError"
    assert log_record.attributes["exception.message"] == "An exception"


COLLECTOR_OPTIONS = Options(collector_endpoint="https://collector.example")


def logging_config(logger_name, handler, propagate=True):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"appsignal": {"()": lambda: handler}},
        "loggers": {logger_name: {"handlers": ["appsignal"], "propagate": propagate}},
    }


def test_add_logging_instrumentation_warns_about_a_duplicate_handler(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))
    handler = LoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(logging_config("duplicate", handler))

    assert logging.getLogger("duplicate").handlers == [handler]
    assert "duplicate" in warning.call_args.args[0]


def test_add_logging_instrumentation_warns_about_a_handler_attached_before_it(
    mocker,
):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    logging.getLogger("duplicate").addHandler(LoggingHandler(level=logging.NOTSET))

    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))

    assert "duplicate" in warning.call_args.args[0]


def test_add_logging_instrumentation_warns_once_per_logger(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))
    handler = LoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(logging_config("duplicate", handler))
    logging.config.dictConfig(logging_config("duplicate", handler))

    assert warning.call_count == 1


def test_start_logging_says_the_sdk_handler_is_deprecated(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    handler = SDKLoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(logging_config("duplicate", handler))

    assert "deprecated" in warning.call_args.args[0]


# An application that attaches the handler itself disables the logging
# instrumentation, so nothing is duplicated, but the handler it was told to
# attach is still the deprecated one.
def test_start_logging_says_so_without_the_logging_instrumentation(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    handler = SDKLoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(logging_config("duplicate", handler))

    assert warning.call_count == 1
    assert "deprecated" in warning.call_args.args[0]


def test_start_logging_says_so_for_a_logger_that_does_not_propagate(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))
    handler = SDKLoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(
        logging_config("duplicate_not_propagating", handler, propagate=False)
    )

    assert warning.call_count == 1
    assert "deprecated" in warning.call_args.args[0]


def test_add_logging_instrumentation_ignores_a_handler_that_is_the_only_one(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))
    handler = LoggingHandler(level=logging.NOTSET)

    logging.config.dictConfig(
        logging_config("duplicate_not_propagating", handler, propagate=False)
    )

    warning.assert_not_called()


def test_add_logging_instrumentation_ignores_a_handler_sending_elsewhere(mocker):
    warning = mocker.patch("appsignal.opentelemetry.logger.warning")
    _start_logging(Config(COLLECTOR_OPTIONS))
    add_logging_instrumentation(Config(COLLECTOR_OPTIONS))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=LoggerProvider())

    logging.config.dictConfig(logging_config("duplicate_elsewhere", handler))

    warning.assert_not_called()


def test_stop_shuts_down_the_started_providers():
    tracer_provider = Mock()
    meter_provider = Mock()
    _providers.extend([tracer_provider, meter_provider])

    stop()

    tracer_provider.shutdown.assert_called_once()
    meter_provider.shutdown.assert_called_once()
    assert _providers == []


def test_stop_shuts_down_the_other_providers_when_one_fails():
    failing_provider = Mock()
    failing_provider.shutdown.side_effect = Exception("Something went wrong")
    other_provider = Mock()
    _providers.extend([failing_provider, other_provider])

    stop()

    other_provider.shutdown.assert_called_once()
    assert _providers == []


def test_stop_without_started_providers():
    stop()

    assert _providers == []


def test_exporter_session_without_a_proxy():
    assert _exporter_session(Config()) is None


def test_exporter_session_with_a_proxy():
    config = Config(
        Options(
            http_proxy="http://proxy.example:3128",
            collector_endpoint="https://collector.example",
        )
    )

    session = _exporter_session(config)

    assert session is not None
    assert session.proxies == {
        "http": "http://proxy.example:3128",
        "https": "http://proxy.example:3128",
    }


def test_exporter_session_with_a_proxy_variable(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:3128")
    config = Config(Options(collector_endpoint="https://collector.example"))

    session = _exporter_session(config)

    assert session is not None
    assert not session.trust_env
    assert session.proxies == {
        "http": "http://proxy.example:3128",
        "https": "http://proxy.example:3128",
    }


def test_exporter_session_with_a_proxy_variable_and_the_agent(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example:3128")

    assert _exporter_session(Config()) is None


def test_exporter_sessions_are_not_shared():
    # Each exporter sends from its own thread, and a session is not thread
    # safe, so they must not share one.
    config = Config(
        Options(
            http_proxy="http://proxy.example:3128",
            collector_endpoint="https://collector.example",
        )
    )

    assert _exporter_session(config) is not _exporter_session(config)


def test_exporter_session_with_a_proxy_and_the_agent():
    config = Config(Options(http_proxy="http://proxy.example:3128"))

    assert _exporter_session(config) is None


def test_exporters_are_given_the_ca_file_and_the_proxy(mocker):
    span_exporter = mocker.patch("appsignal.opentelemetry.OTLPSpanExporter")
    metric_exporter = mocker.patch("appsignal.opentelemetry.OTLPMetricExporter")
    log_exporter = mocker.patch("appsignal.opentelemetry.OTLPLogExporter")

    config = Config(
        Options(
            ca_file_path="/path/to/cacert.pem",
            http_proxy="http://proxy.example:3128",
            collector_endpoint="https://collector.example",
        )
    )

    _start_tracer(config)
    _start_metrics(config)
    _start_logging(config)

    for exporter in [span_exporter, metric_exporter, log_exporter]:
        kwargs = exporter.call_args.kwargs
        assert kwargs["certificate_file"] == "/path/to/cacert.pem"
        assert kwargs["session"].proxies == {
            "http": "http://proxy.example:3128",
            "https": "http://proxy.example:3128",
        }


def test_collector_data_goes_through_the_proxy(recording_server, mocker):
    proxy = recording_server()
    config = Config(
        Options(
            http_proxy=proxy.url,
            collector_endpoint="http://collector.example",
        )
    )

    export_a_span(config, mocker)

    assert proxy.paths == ["http://collector.example/v1/traces"]


def test_collector_data_goes_through_the_proxy_variable(
    recording_server, monkeypatch, mocker
):
    proxy = recording_server()
    monkeypatch.setenv("HTTP_PROXY", proxy.url)
    config = Config(Options(collector_endpoint="http://collector.example"))

    export_a_span(config, mocker)

    assert proxy.paths == ["http://collector.example/v1/traces"]


def test_collector_data_goes_through_the_option_over_the_proxy_variable(
    recording_server, monkeypatch, mocker
):
    option_proxy = recording_server()
    variable_proxy = recording_server()
    monkeypatch.setenv("HTTP_PROXY", variable_proxy.url)
    config = Config(
        Options(
            http_proxy=option_proxy.url,
            collector_endpoint="http://collector.example",
        )
    )

    export_a_span(config, mocker)

    assert option_proxy.paths == ["http://collector.example/v1/traces"]
    assert variable_proxy.paths == []


def test_agent_data_does_not_go_through_the_proxy(recording_server, mocker):
    proxy = recording_server()
    agent = recording_server()
    config = Config(Options(http_proxy=proxy.url, opentelemetry_port=agent.port))

    export_a_span(config, mocker)

    assert agent.paths == ["/v1/traces"]
    assert proxy.paths == []
