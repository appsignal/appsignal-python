from appsignal.client import Client
from appsignal.config import Config, Options
from appsignal.transmitter import transmit


options = Options(
    push_api_key="some-push-api-key",
    name="some-app",
    environment="staging",
    hostname="beepboop.local",
)

config = Config(options)


def test_transmitter_adds_query_parameters_from_confing(mocker):
    mock_request = mocker.patch("requests.Session.post")

    transmit("https://example.url/", config=config)

    assert mock_request.called
    assert "https://example.url/?" in mock_request.call_args[0][0]
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in mock_request.call_args[0][0]
    assert "environment=staging" in mock_request.call_args[0][0]
    assert "hostname=beepboop.local" in mock_request.call_args[0][0]
    assert "name=some-app" in mock_request.call_args[0][0]


def test_transmitter_get_config_from_global_client(mocker):
    mock_request = mocker.patch("requests.Session.post")

    Client(**options)

    transmit("https://example.url/")

    assert mock_request.called
    assert "https://example.url/?" in mock_request.call_args[0][0]
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in mock_request.call_args[0][0]
    assert "environment=staging" in mock_request.call_args[0][0]
    assert "hostname=beepboop.local" in mock_request.call_args[0][0]
    assert "name=some-app" in mock_request.call_args[0][0]


def test_transmitter_send_body_as_json(mocker):
    mock_request = mocker.patch("requests.Session.post")

    transmit("https://example.url/", json={"key": "value"}, config=config)

    assert mock_request.called
    assert mock_request.call_args[1]["json"] == {"key": "value"}


def test_transmitter_send_body_as_ndjson(mocker):
    mock_request = mocker.patch("requests.Session.post")

    transmit(
        "https://example.url/", ndjson=[{"key": "value"}, {"foo": "bar"}], config=config
    )

    assert mock_request.called
    assert mock_request.call_args[1]["data"] == '{"key": "value"}\n{"foo": "bar"}'
    assert mock_request.call_args[1]["headers"] == {
        "Content-Type": "application/x-ndjson"
    }


def test_transmitter_set_proxies_from_config(mocker):
    mock_request = mocker.patch("requests.Session.post")

    transmit("https://example.url/", config=config)

    assert mock_request.called
    assert mock_request.call_args[1]["proxies"] == {}

    mock_request = mocker.patch("requests.Session.post")

    with_proxy = Config(Options(**options, http_proxy="http://proxy.local:1234"))
    transmit("https://example.url/", config=with_proxy)

    assert mock_request.called
    assert mock_request.call_args[1]["proxies"] == {
        "http": "http://proxy.local:1234",
        "https": "http://proxy.local:1234",
    }


def test_transmitter_set_proxies_from_the_proxy_variable(mocker, monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.local:1234")
    mock_request = mocker.patch("requests.Session.post")

    transmit("https://example.url/", config=config)

    assert mock_request.call_args[1]["proxies"] == {
        "http": "http://proxy.local:1234",
        "https": "http://proxy.local:1234",
    }


def test_transmitter_sends_through_the_option_over_the_proxy_variable(
    recording_server, monkeypatch
):
    option_proxy = recording_server()
    variable_proxy = recording_server()
    monkeypatch.setenv("HTTP_PROXY", variable_proxy.url)
    with_proxy = Config(Options(**options, http_proxy=option_proxy.url))

    transmit("http://example.url/", config=with_proxy)

    assert len(option_proxy.paths) == 1
    assert option_proxy.paths[0].startswith("http://example.url/?")
    assert variable_proxy.paths == []


def test_transmitter_set_cert_from_config(mocker):
    mock_request = mocker.patch("requests.Session.post")

    transmit("https://example.url/", config=config)

    assert mock_request.called
    assert mock_request.call_args[1]["verify"].endswith("/cacert.pem")

    with_ca = Config(Options(**options, ca_file_path="path/to/ca.pem"))

    transmit("https://example.url/", config=with_ca)

    assert mock_request.called
    assert mock_request.call_args[1]["verify"] == "path/to/ca.pem"
