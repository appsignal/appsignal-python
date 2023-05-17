from appsignal.client import Client

import os
import re
from logging import ERROR, WARNING, INFO, DEBUG


def test_client_options_merge_sources():
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some_key"
    client = Client(name="MyApp")
    assert client._config.options["name"] == "MyApp"
    assert client._config.options["push_api_key"] == "some_key"
    assert "app_path" in client._config.options


def test_client_active():
    client = Client(
        active=True, name="MyApp", request_headers=["accept", "x-custom-header"]
    )
    assert client._config.options["active"] is True
    assert client._config.options["name"] == "MyApp"
    assert client._config.options["request_headers"] == ["accept", "x-custom-header"]
    client.start()

    # Sets the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert os.environ.get("_APPSIGNAL_APP_NAME") == "MyApp"
    assert (
        os.environ.get("OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST")
        == "accept,x-custom-header"
    )


def test_client_active_without_request_headers():
    client = Client(active=True, name="MyApp", request_headers=None)
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


def test_logger_default_level():
    client = Client()
    assert client._logger.getEffectiveLevel() == INFO

    client = Client(log_level="info")
    assert client._logger.getEffectiveLevel() == INFO


def test_logger_error_level():
    client = Client(log_level="error")
    assert client._logger.getEffectiveLevel() == ERROR


def test_logger_warning_level():
    client = Client(log_level="warning")
    assert client._logger.getEffectiveLevel() == WARNING


def test_logger_debug_level():
    client = Client(log_level="debug")
    assert client._logger.getEffectiveLevel() == DEBUG


def test_logger_trace_level():
    client = Client(log_level="trace")
    assert client._logger.getEffectiveLevel() == DEBUG


def test_logger_file(tmp_path):
    log_path = tmp_path
    log_file_path = os.path.join(log_path, "appsignal.log")

    client = Client(log_path=log_path)
    logger = client._logger
    logger.info("test me")

    with open(log_file_path) as file:
        contents = file.read()

    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[INFO\] test me"
    )
    assert log_line_regex.search(contents)


def test_logger_stdout(capsys):
    client = Client(log="stdout")
    logger = client._logger
    logger.info("test me")

    captured = capsys.readouterr()
    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[appsignal\]"
        r"\[INFO\] test me"
    )
    assert log_line_regex.search(captured.out)


def test_logger_stdout_fallback(capsys, mocker):
    # Make any path appear unwritable so it will fall back to the STDOUT logger
    mocker.patch("os.access", return_value=False)

    client = Client(log="file", log_path=None)
    logger = client._logger
    logger.info("test me")

    captured = capsys.readouterr()
    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[appsignal\]"
        r"\[INFO\] test me"
    )
    assert log_line_regex.search(captured.out)
