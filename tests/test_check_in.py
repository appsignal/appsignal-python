from time import sleep

from pytest import raises

from appsignal import Heartbeat, heartbeat
from appsignal.check_in import Cron, cron
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


def test_cron_start_and_finish_when_appsignal_is_not_active_sends_nothing(mocker):
    requests_mock = mock_requests(mocker)
    init_client(active=False)

    cron = Cron("some-cron-checkin")
    cron.start()
    cron.finish()

    assert not requests_mock.called


def test_cron_start_sends_cron_checkin_start_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron = Cron("some-cron-checkin")
    cron.start()

    assert requests_mock.called
    assert (
        "https://appsignal-endpoint.net/check_ins/json?"
        in requests_mock.call_args[0][0]
    )
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in requests_mock.call_args[0][0]
    assert "environment=staging" in requests_mock.call_args[0][0]
    assert "hostname=beepboop.local" in requests_mock.call_args[0][0]
    assert "name=some-app" in requests_mock.call_args[0][0]

    assert requests_mock.call_args[1]["json"]["identifier"] == "some-cron-checkin"
    assert requests_mock.call_args[1]["json"]["kind"] == "start"
    assert isinstance(requests_mock.call_args[1]["json"]["timestamp"], int)
    assert isinstance(requests_mock.call_args[1]["json"]["digest"], str)
    assert requests_mock.call_args[1]["json"]["check_in_type"] == "cron"


def test_cron_finish_sends_cron_checkin_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron = Cron("some-cron-checkin")
    cron.finish()

    assert requests_mock.called
    assert (
        "https://appsignal-endpoint.net/check_ins/json?"
        in requests_mock.call_args[0][0]
    )
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in requests_mock.call_args[0][0]
    assert "environment=staging" in requests_mock.call_args[0][0]
    assert "hostname=beepboop.local" in requests_mock.call_args[0][0]
    assert "name=some-app" in requests_mock.call_args[0][0]

    assert requests_mock.call_args[1]["json"]["identifier"] == "some-cron-checkin"
    assert requests_mock.call_args[1]["json"]["kind"] == "finish"
    assert isinstance(requests_mock.call_args[1]["json"]["timestamp"], int)
    assert isinstance(requests_mock.call_args[1]["json"]["digest"], str)
    assert requests_mock.call_args[1]["json"]["check_in_type"] == "cron"


def test_cron_sends_cron_checkin_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron("some-cron-checkin")

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 1

    assert requests_mock.call_args[1]["json"]["identifier"] == "some-cron-checkin"
    assert requests_mock.call_args[1]["json"]["kind"] == "finish"


def test_cron_with_function_sends_cron_checkin_start_and_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        sleep(1.1)
        return "output"

    assert cron("some-cron-checkin", some_function) == "output"

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 2

    assert (
        requests_mock.call_args_list[0][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[0][1]["json"]["kind"] == "start"
    assert (
        requests_mock.call_args_list[1][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[1][1]["json"]["kind"] == "finish"
    assert (
        requests_mock.call_args_list[0][1]["json"]["timestamp"]
        < requests_mock.call_args_list[1][1]["json"]["timestamp"]
    )
    assert (
        requests_mock.call_args_list[0][1]["json"]["digest"]
        == requests_mock.call_args_list[1][1]["json"]["digest"]
    )
    assert requests_mock.call_args_list[0][1]["json"]["check_in_type"] == "cron"
    assert requests_mock.call_args_list[1][1]["json"]["check_in_type"] == "cron"


def test_cron_with_function_does_not_send_cron_checkin_finish_event_on_exception(
    mocker,
):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        raise Exception("Whoops!")

    with raises(Exception, match="Whoops!"):
        cron("some-cron-checkin", some_function)

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 1

    assert (
        requests_mock.call_args_list[0][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[0][1]["json"]["kind"] == "start"


def test_cron_context_manager_sends_cron_checkin_start_and_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    with Cron("some-cron-checkin"):
        sleep(1.1)

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 2

    assert (
        requests_mock.call_args_list[0][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[0][1]["json"]["kind"] == "start"
    assert (
        requests_mock.call_args_list[1][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[1][1]["json"]["kind"] == "finish"
    assert (
        requests_mock.call_args_list[0][1]["json"]["timestamp"]
        < requests_mock.call_args_list[1][1]["json"]["timestamp"]
    )
    assert (
        requests_mock.call_args_list[0][1]["json"]["digest"]
        == requests_mock.call_args_list[1][1]["json"]["digest"]
    )
    assert requests_mock.call_args_list[0][1]["json"]["check_in_type"] == "cron"
    assert requests_mock.call_args_list[1][1]["json"]["check_in_type"] == "cron"


def test_cron_context_manager_does_not_send_cron_checkin_finish_event_on_exception(
    mocker,
):
    requests_mock = mock_requests(mocker)
    init_client()

    with raises(Exception, match="Whoops!"):
        with Cron("some-cron-checkin"):
            raise Exception("Whoops!")

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 1

    assert (
        requests_mock.call_args_list[0][1]["json"]["identifier"] == "some-cron-checkin"
    )
    assert requests_mock.call_args_list[0][1]["json"]["kind"] == "start"


def test_cron_logs_failure_to_send_event_when_status_code(mocker):
    mock_requests(mocker, status_code=500)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "error")

    cron = Cron("some-cron-checkin")
    cron.start()

    assert internal_logger_mock.called
    assert len(internal_logger_mock.call_args_list) == 1
    assert (
        "Failed to transmit cron check-in start event: status code was 500"
        in internal_logger_mock.call_args[0][0]
    )


def test_cron_logs_failure_to_send_event_when_exception(mocker):
    mock_requests(mocker, raise_exception=True)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "error")

    cron = Cron("some-cron-checkin")
    cron.start()

    assert internal_logger_mock.called
    assert len(internal_logger_mock.call_args_list) == 1
    assert (
        "Failed to transmit cron check-in start event: Whoops!"
        in internal_logger_mock.call_args[0][0]
    )


def test_heartbeat_helper_behaves_like_cron_helper(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        return "output"

    assert heartbeat("some-heartbeat", some_function) == "output"

    assert requests_mock.called
    assert len(requests_mock.call_args_list) == 2

    assert requests_mock.call_args_list[0][1]["json"]["identifier"] == "some-heartbeat"
    assert requests_mock.call_args_list[0][1]["json"]["kind"] == "start"
    assert requests_mock.call_args_list[1][1]["json"]["identifier"] == "some-heartbeat"
    assert requests_mock.call_args_list[1][1]["json"]["kind"] == "finish"


def test_heartbeat_helper_emits_deprecation_warning(mocker, reset_heartbeat_warnings):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    heartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        assert mock.called
        assert len(mock.call_args_list) == 1
        assert "The helper `heartbeat` has been deprecated" in mock.call_args[0][0]


def test_heartbeat_helper_only_emits_deprecation_warning_once(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    heartbeat("some-heartbeat")
    heartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        assert mock.call_count == 1


def test_heartbeat_class_returns_cron_instance():
    cron_instance = Heartbeat("some-heartbeat")
    assert isinstance(cron_instance, Cron)


def test_cron_instance_as_instance_of_heartbeat():
    for instance_class in [Cron, Heartbeat]:
        for checked_class in [Cron, Heartbeat]:
            assert isinstance(instance_class("some-instance"), checked_class)


def test_heartbeat_class_emits_deprecation_warning(mocker, reset_heartbeat_warnings):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    Heartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        assert mock.called
        assert len(mock.call_args_list) == 1
        assert "The class `Heartbeat` has been deprecated" in mock.call_args[0][0]


def test_heartbeat_class_only_emits_deprecation_warning_once(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    Heartbeat("some-heartbeat")
    Heartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        assert mock.call_count == 1
