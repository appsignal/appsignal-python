from __future__ import annotations

import os
import signal
from unittest.mock import call, mock_open, patch

from appsignal.agent import Agent
from appsignal.binary import NoopBinary
from appsignal.client import Client


def test_client_options_merge_sources():
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some_key"
    client = Client(name="MyApp")
    assert client._config.options["name"] == "MyApp"
    assert client._config.options["push_api_key"] == "some_key"
    assert "app_path" in client._config.options


def test_client_agent_inactive():
    client = Client(active=False, name="MyApp")
    assert client._config.options["active"] is False
    assert client._config.is_active() is False
    client.start()

    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert type(client._binary) is Agent
    assert client._binary.active is False


def test_client_agent_active():
    client = Client(active=True, name="MyApp", push_api_key="000")
    assert client._config.options["active"] is True
    assert client._config.is_active() is True
    client.start()

    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert type(client._binary) is Agent
    assert client._binary.active is True


def test_client_agent_active_invalid():
    client = Client(active=True, name="MyApp", push_api_key="")
    assert client._config.option("active") is True
    assert client._config.is_active() is False
    client.start()

    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert type(client._binary) is Agent
    assert client._binary.active is False


def test_client_active_noopbinary_when_collector_endpoint_set():
    client = Client(
        active=True,
        name="MyApp",
        push_api_key="0000-0000-0000-0000",
        request_headers=["accept", "x-custom-header"],
        collector_endpoint="https://custom-endpoint.appsignal.com",
    )

    client.start()

    assert type(client._binary) is NoopBinary
    assert client._binary.active

    # Does not set the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert os.environ.get("_APPSIGNAL_APP_NAME") is None
    assert os.environ.get("_APPSIGNAL_PUSH_API_KEY") is None

    # Sets the OpenTelemetry config environment variables
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        == "accept,x-custom-header"
    )


def test_client_active():
    client = Client(
        active=True,
        name="MyApp",
        request_headers=["accept", "x-custom-header"],
        push_api_key="0000-0000-0000-0000",
    )
    assert client._config.options["active"] is True
    assert client._config.options["name"] == "MyApp"
    assert client._config.options["request_headers"] == ["accept", "x-custom-header"]
    assert client._config.options["push_api_key"] == "0000-0000-0000-0000"
    assert client._config.is_active() is True
    client.start()

    # Sets the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert os.environ.get("_APPSIGNAL_APP_NAME") == "MyApp"
    assert os.environ.get("_APPSIGNAL_PUSH_API_KEY") == "0000-0000-0000-0000"

    # Sets the OpenTelemetry config environment variables
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        == "accept,x-custom-header"
    )

    assert type(client._binary) is Agent
    assert client._binary.active


def test_client_active_without_request_headers():
    client = Client(active=True, name="MyApp", push_api_key="000", request_headers=None)
    assert client._config.options["active"] is True
    assert client._config.options["name"] == "MyApp"
    assert client._config.options["request_headers"] is None
    client.start()

    # Sets the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert os.environ.get("_APPSIGNAL_APP_NAME") == "MyApp"
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        is None
    )


def test_client_inactive():
    client = Client(active=False, name="MyApp")
    assert client._config.options["active"] is False
    assert client._config.options["name"] == "MyApp"
    client.start()

    # Does not set the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert os.environ.get("_APPSIGNAL_APP_NAME") is None
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        is None
    )


@patch("time.sleep", return_value=None)
@patch("os.kill", return_value=None)
@patch("builtins.open", new_callable=mock_open, read_data="123456;running;123\n")
def test_client_stop_kills_agent(mock_open, mock_kill, mock_sleep):
    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    client.stop()

    mock_kill.assert_has_calls(
        [
            call(123, signal.SIGTERM),
        ]
    )


def test_client_stop_stops_scheduler(mocker):
    # use mocker to check that the `stop` method in the `_scheduler` global variable
    # in `check_in.scheduler._scheduler` is called

    stop_mock = mocker.patch("appsignal.check_in.scheduler._scheduler.stop")

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    stop_mock.assert_not_called()

    client.stop()

    stop_mock.assert_called_once()
