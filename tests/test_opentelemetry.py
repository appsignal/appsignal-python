from __future__ import annotations

from typing import List, cast
from unittest.mock import Mock

from appsignal.config import Config, Options
from appsignal.opentelemetry import (
    _exporter_session,
    _providers,
    _start_logging,
    _start_metrics,
    _start_tracer,
    add_instrumentations,
    stop,
)


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
                List[Config.DefaultInstrumentation],
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
    config = Config(Options(http_proxy="http://proxy.example:3128"))

    session = _exporter_session(config)

    assert session is not None
    assert session.proxies == {
        "http": "http://proxy.example:3128",
        "https": "http://proxy.example:3128",
    }


def test_exporter_sessions_are_not_shared():
    # Each exporter sends from its own thread, and a session is not thread
    # safe, so they must not share one.
    config = Config(Options(http_proxy="http://proxy.example:3128"))

    assert _exporter_session(config) is not _exporter_session(config)


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
