from __future__ import annotations

import os
import signal
from unittest.mock import call, mock_open, patch

from appsignal import probes
from appsignal.agent import Agent
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
    assert type(client._agent) is Agent
    assert client._agent.active is False


def test_client_agent_active():
    client = Client(active=True, name="MyApp", push_api_key="000")
    assert client._config.options["active"] is True
    assert client._config.is_active() is True
    client.start()

    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert type(client._agent) is Agent
    assert client._agent.active is True


def test_client_agent_active_invalid():
    client = Client(active=True, name="MyApp", push_api_key="")
    assert client._config.option("active") is True
    assert client._config.is_active() is False
    client.start()

    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert type(client._agent) is Agent
    assert client._agent.active is False


def test_client_active_when_collector_endpoint_set():
    client = Client(
        active=True,
        name="MyApp",
        push_api_key="0000-0000-0000-0000",
        request_headers=["accept", "x-custom-header"],
        collector_endpoint="https://custom-endpoint.appsignal.com",
    )

    client.start()

    # Starts the agent, which reports what the collector does not
    assert type(client._agent) is Agent
    assert client._agent.active

    # Sets the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert os.environ.get("_APPSIGNAL_APP_NAME") == "MyApp"
    assert os.environ.get("_APPSIGNAL_PUSH_API_KEY") == "0000-0000-0000-0000"

    # Does not let the agent listen for OpenTelemetry data, because it is sent
    # to the collector instead, on a port that defaults to the same number
    assert os.environ.get("_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP") == "false"

    # Sets the OpenTelemetry config environment variables
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        == "accept,x-custom-header"
    )


def test_client_starts_opentelemetry_in_collector_mode_without_the_agent(mocker):
    mocker.patch("appsignal.agent.Agent.start")
    start_opentelemetry = mocker.patch("appsignal.client.start_opentelemetry")
    warning = mocker.patch("appsignal.internal_logger.warning")

    client = Client(
        active=True,
        name="MyApp",
        push_api_key="0000-0000-0000-0000",
        collector_endpoint="https://custom-endpoint.appsignal.com",
    )

    client.start()

    assert client._agent.active is False
    start_opentelemetry.assert_called_once()
    assert any(
        "The AppSignal agent did not start" in call.args[0]
        for call in warning.call_args_list
    )


def test_client_agent_unavailable_message_in_collector_mode(mocker, capsys):
    mocker.patch(
        "appsignal.agent.Agent.architecture_and_platform", return_value=["any"]
    )

    client = Client(
        active=True,
        name="MyApp",
        push_api_key="0000-0000-0000-0000",
        collector_endpoint="https://custom-endpoint.appsignal.com",
    )
    client.start()

    # Data still reaches the collector without the agent, so the message must
    # not say that nothing is sent.
    output = capsys.readouterr().out
    assert "AppSignal agent is not available for this platform." in output
    assert "no data will be sent to AppSignal" not in output


def test_client_agent_unavailable_message_in_agent_mode(mocker, capsys):
    mocker.patch(
        "appsignal.agent.Agent.architecture_and_platform", return_value=["any"]
    )

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    output = capsys.readouterr().out
    assert "AppSignal agent is not available for this platform." in output
    assert "no data will be sent to AppSignal" in output


def test_client_does_not_start_opentelemetry_without_the_agent(mocker):
    mocker.patch("appsignal.agent.Agent.start")
    start_opentelemetry = mocker.patch("appsignal.client.start_opentelemetry")

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")

    client.start()

    assert client._agent.active is False
    start_opentelemetry.assert_not_called()


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

    # Lets the agent listen for OpenTelemetry data, because it is sent there
    assert os.environ.get("_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP") == "true"

    # Sets the OpenTelemetry config environment variables
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        == "accept,x-custom-header"
    )

    assert type(client._agent) is Agent
    assert client._agent.active


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
    # Waits for the agent to send the trace data it still holds
    assert call(2) in mock_sleep.call_args_list


@patch("time.sleep", return_value=None)
@patch("os.kill", return_value=None)
@patch("builtins.open", new_callable=mock_open, read_data="123456;running;123\n")
def test_client_stop_does_not_wait_for_the_agent_in_collector_mode(
    mock_open, mock_kill, mock_sleep
):
    client = Client(
        active=True,
        name="MyApp",
        push_api_key="0000-0000-0000-0000",
        collector_endpoint="https://custom-endpoint.appsignal.com",
    )
    client.start()

    client.stop()

    mock_kill.assert_has_calls(
        [
            call(123, signal.SIGTERM),
        ]
    )
    # Does not wait for the agent, which only holds host, NGINX and StatsD
    # metrics when a collector is used
    assert call(2) not in mock_sleep.call_args_list


@patch("time.sleep", return_value=None)
@patch("os.kill", return_value=None)
@patch("builtins.open", new_callable=mock_open, read_data="123456;running;123\n")
def test_client_stop_only_stops_the_agent_once(mock_open, mock_kill, mock_sleep):
    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    client.stop()
    client.stop()

    # The second stop has no agent left to signal, and the process it would
    # signal may belong to something else by then.
    assert mock_kill.call_count == 1


def test_client_stop_does_not_kill_an_agent_it_did_not_start(mocker):
    kill = mocker.patch("os.kill")

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")

    client.stop()

    kill.assert_not_called()


def test_client_stop_stops_probes(mocker):
    mocker.patch("appsignal.probes._initial_wait_time").return_value = 0.001
    mocker.patch("appsignal.probes._wait_time").return_value = 0.001

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    assert probes._thread is not None

    client.stop()

    assert probes._thread is None


def test_client_stop_stops_probes_before_opentelemetry(mocker):
    # Probes report through the metric helpers, which write to the meter
    # provider, so they have to stop before it is shut down.
    calls = []

    mocker.patch(
        "appsignal.client.stop_probes",
        side_effect=lambda: calls.append("probes"),
    )
    mocker.patch(
        "appsignal.client.stop_opentelemetry",
        side_effect=lambda: calls.append("opentelemetry"),
    )

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    client.stop()

    assert calls == ["probes", "opentelemetry"]


def test_client_stop_without_started_probes():
    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")

    client.stop()

    assert probes._thread is None


def test_client_stop_shuts_down_opentelemetry_before_the_agent(mocker):
    # When the agent is used, it is the endpoint that OpenTelemetry data is
    # sent to, so it has to still be running when that data is flushed.
    calls = []

    mocker.patch(
        "appsignal.client.stop_opentelemetry",
        side_effect=lambda: calls.append("opentelemetry"),
    )
    mocker.patch(
        "appsignal.agent.Agent.stop",
        side_effect=lambda config: calls.append("agent"),
    )

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    client.stop()

    assert calls == ["opentelemetry", "agent"]


def test_client_stop_stops_scheduler(mocker):
    # use mocker to check that the `stop` method in the `_scheduler` global variable
    # in `check_in.scheduler._scheduler` is called

    stop_mock = mocker.patch("appsignal.check_in.scheduler._scheduler.stop")

    client = Client(active=True, name="MyApp", push_api_key="0000-0000-0000-0000")
    client.start()

    stop_mock.assert_not_called()

    client.stop()

    stop_mock.assert_called_once()
