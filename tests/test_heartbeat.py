from time import sleep

from pytest import raises

from appsignal.client import Client
from appsignal.heartbeat import Heartbeat, heartbeat


def init_client(active=True):
    Client(
        push_api_key="some-push-api-key",
        name="some-app",
        environment="staging",
        hostname="beepboop.local",
        active=active,
    )


def test_start_finish_when_appsignal_is_not_active_sends_nothing(mocker):
    mock_request = mocker.patch("requests.post")
    init_client(active=False)

    heartbeat = Heartbeat("some-heartbeat")
    heartbeat.start()
    heartbeat.finish()

    assert not mock_request.called


def test_start_sends_heartbeat_start_event(mocker):
    mock_request = mocker.patch("requests.post")
    init_client()

    heartbeat = Heartbeat("some-heartbeat")
    heartbeat.start()

    assert mock_request.called
    assert (
        "https://appsignal-endpoint.net/heartbeats/json?"
        in mock_request.call_args[0][0]
    )
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in mock_request.call_args[0][0]
    assert "environment=staging" in mock_request.call_args[0][0]
    assert "hostname=beepboop.local" in mock_request.call_args[0][0]
    assert "name=some-app" in mock_request.call_args[0][0]

    assert mock_request.call_args[1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args[1]["json"]["kind"] == "start"
    assert isinstance(mock_request.call_args[1]["json"]["timestamp"], int)
    assert isinstance(mock_request.call_args[1]["json"]["id"], str)


def test_finish_sends_heartbeat_finish_event(mocker):
    mock_request = mocker.patch("requests.post")
    init_client()

    heartbeat = Heartbeat("some-heartbeat")
    heartbeat.finish()

    assert mock_request.called
    assert (
        "https://appsignal-endpoint.net/heartbeats/json?"
        in mock_request.call_args[0][0]
    )
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in mock_request.call_args[0][0]
    assert "environment=staging" in mock_request.call_args[0][0]
    assert "hostname=beepboop.local" in mock_request.call_args[0][0]
    assert "name=some-app" in mock_request.call_args[0][0]

    assert mock_request.call_args[1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args[1]["json"]["kind"] == "finish"
    assert isinstance(mock_request.call_args[1]["json"]["timestamp"], int)
    assert isinstance(mock_request.call_args[1]["json"]["id"], str)


def test_heartbeat_sends_heartbeat_finish_event(mocker):
    mock_request = mocker.patch("requests.post")
    init_client()

    heartbeat("some-heartbeat")

    assert mock_request.called
    assert len(mock_request.call_args_list) == 1

    assert mock_request.call_args[1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args[1]["json"]["kind"] == "finish"


def test_heartbeat_with_function_sends_heartbeat_start_and_finish_event(mocker):
    mock_request = mocker.patch("requests.post")
    init_client()

    def some_function():
        sleep(1.1)
        return "output"

    assert heartbeat("some-heartbeat", some_function) == "output"

    assert mock_request.called
    assert len(mock_request.call_args_list) == 2

    assert mock_request.call_args_list[0][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[0][1]["json"]["kind"] == "start"
    assert mock_request.call_args_list[1][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[1][1]["json"]["kind"] == "finish"
    assert (
        mock_request.call_args_list[0][1]["json"]["timestamp"]
        < mock_request.call_args_list[1][1]["json"]["timestamp"]
    )
    assert (
        mock_request.call_args_list[0][1]["json"]["id"]
        == mock_request.call_args_list[1][1]["json"]["id"]
    )


def test_heartbeat_with_function_does_not_send_heartbeat_finish_event_on_exception(
    mocker,
):
    mock_request = mocker.patch("requests.post")
    init_client()

    def some_function():
        raise Exception("Whoops!")

    with raises(Exception, match="Whoops!"):
        heartbeat("some-heartbeat", some_function)

    assert mock_request.called
    assert len(mock_request.call_args_list) == 1

    assert mock_request.call_args_list[0][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[0][1]["json"]["kind"] == "start"


def test_heartbeat_context_manager_sends_heartbeat_start_and_finish_event(mocker):
    mock_request = mocker.patch("requests.post")
    init_client()

    with Heartbeat("some-heartbeat"):
        sleep(1.1)

    assert mock_request.called
    assert len(mock_request.call_args_list) == 2

    assert mock_request.call_args_list[0][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[0][1]["json"]["kind"] == "start"
    assert mock_request.call_args_list[1][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[1][1]["json"]["kind"] == "finish"
    assert (
        mock_request.call_args_list[0][1]["json"]["timestamp"]
        < mock_request.call_args_list[1][1]["json"]["timestamp"]
    )
    assert (
        mock_request.call_args_list[0][1]["json"]["id"]
        == mock_request.call_args_list[1][1]["json"]["id"]
    )


def test_heartbeat_context_manager_does_not_send_heartbeat_finish_event_on_exception(
    mocker,
):
    mock_request = mocker.patch("requests.post")
    init_client()

    with raises(Exception, match="Whoops!"):
        with Heartbeat("some-heartbeat"):
            raise Exception("Whoops!")

    assert mock_request.called
    assert len(mock_request.call_args_list) == 1

    assert mock_request.call_args_list[0][1]["json"]["name"] == "some-heartbeat"
    assert mock_request.call_args_list[0][1]["json"]["kind"] == "start"
