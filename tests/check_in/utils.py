from appsignal import ndjson
from appsignal.client import Client


def init_client(active=True):
    Client(
        push_api_key="some-push-api-key",
        name="some-app",
        environment="staging",
        hostname="beepboop.local",
        active=active,
    )


def mock_requests(mocker, status_code=200, raise_exception=False):
    requests_mock = mocker.patch("requests.post")
    requests_mock.return_value.status_code = status_code
    if raise_exception:

        def side_effect(*args, **kwargs):
            raise Exception("Whoops!")

        requests_mock.side_effect = side_effect

    return requests_mock


def mock_internal_logger(mocker, level):
    return mocker.patch(f"appsignal.internal_logger.{level}")


def mock_print(mocker):
    return mocker.patch("builtins.print")


def assert_called_once(mock):
    assert_called_times(mock, 1)


def assert_called_times(requests_mock, times: int):
    assert requests_mock.called
    assert len(requests_mock.call_args_list) == times


def assert_called_at_least(requests_mock, times: int):
    assert requests_mock.called
    assert len(requests_mock.call_args_list) >= times


def received_events(request_mock, call: int = 0):
    data = request_mock.call_args_list[call][1]["data"]
    return ndjson.loads(data)


def received_url(request_mock, call: int = 0):
    return request_mock.call_args_list[call][0][0]


def received_messages(internal_logger_mock):
    return [args[0][0] for args in internal_logger_mock.call_args_list]


def assert_url_config(url):
    assert "https://appsignal-endpoint.net/check_ins/json?" in url
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in url
    assert "environment=staging" in url
    assert "hostname=beepboop.local" in url
    assert "name=some-app" in url
