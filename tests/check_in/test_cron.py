from time import sleep

from pytest import raises

from appsignal import Heartbeat as DeprecatedHeartbeat
from appsignal import heartbeat as deprecated_heartbeat
from appsignal.check_in import Cron, cron
from appsignal.check_in.scheduler import scheduler

from .utils import (
    assert_called_once,
    assert_called_times,
    assert_url_config,
    init_client,
    mock_internal_logger,
    mock_print,
    mock_requests,
    received_events,
    received_messages,
    received_url,
)


def assert_cron_event(event, kind):
    assert event["identifier"] == "some-cron-checkin"
    assert event["kind"] == kind
    assert isinstance(event["timestamp"], int)
    assert isinstance(event["digest"], str)
    assert event["check_in_type"] == "cron"


def test_cron_start_and_finish_when_appsignal_is_not_active_sends_nothing(mocker):
    requests_mock = mock_requests(mocker)
    init_client(active=False)

    cron = Cron("some-cron-checkin")
    cron.start()
    cron.finish()
    scheduler().stop()

    assert not requests_mock.called


def test_cron_start_sends_cron_checkin_start_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron = Cron("some-cron-checkin")
    cron.start()
    scheduler().stop()

    assert_called_once(requests_mock)
    assert_url_config(received_url(requests_mock))

    events = received_events(requests_mock)
    assert len(events) == 1
    assert_cron_event(events[0], "start")


def test_cron_finish_sends_cron_checkin_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron = Cron("some-cron-checkin")
    cron.finish()
    scheduler().stop()

    assert_called_once(requests_mock)

    assert_url_config(received_url(requests_mock))

    events = received_events(requests_mock)
    assert len(events) == 1
    assert_cron_event(events[0], "finish")


def test_cron_sends_cron_checkin_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    cron("some-cron-checkin")
    scheduler().stop()

    assert_called_once(requests_mock)

    events = received_events(requests_mock)
    assert len(events) == 1
    assert_cron_event(events[0], "finish")


def test_cron_with_function_sends_cron_checkin_start_and_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        sleep(1.1)
        return "output"

    assert cron("some-cron-checkin", some_function) == "output"

    scheduler().stop()

    assert_called_times(requests_mock, 2)

    first_events = received_events(requests_mock, call=0)
    assert len(first_events) == 1
    assert_cron_event(first_events[0], "start")
    start_event = first_events[0]

    second_events = received_events(requests_mock, call=1)
    assert len(second_events) == 1
    assert_cron_event(second_events[0], "finish")
    finish_event = second_events[0]

    assert start_event["timestamp"] < finish_event["timestamp"]
    assert start_event["digest"] == finish_event["digest"]


def test_cron_with_function_does_not_send_cron_checkin_finish_event_on_exception(
    mocker,
):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        raise Exception("Whoops!")

    with raises(Exception, match="Whoops!"):
        cron("some-cron-checkin", some_function)

    scheduler().stop()

    assert_called_once(requests_mock)
    events = received_events(requests_mock)
    assert len(events) == 1
    assert_cron_event(events[0], "start")


def test_cron_context_manager_sends_cron_checkin_start_and_finish_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    with Cron("some-cron-checkin"):
        sleep(1.1)

    scheduler().stop()

    assert_called_times(requests_mock, 2)

    first_events = received_events(requests_mock, call=0)
    assert len(first_events) == 1
    assert_cron_event(first_events[0], "start")
    start_event = first_events[0]

    second_events = received_events(requests_mock, call=1)
    assert len(second_events) == 1
    assert_cron_event(second_events[0], "finish")
    finish_event = second_events[0]

    assert start_event["timestamp"] < finish_event["timestamp"]
    assert start_event["digest"] == finish_event["digest"]


def test_cron_context_manager_does_not_send_cron_checkin_finish_event_on_exception(
    mocker,
):
    requests_mock = mock_requests(mocker)
    init_client()

    with raises(Exception, match="Whoops!"):
        with Cron("some-cron-checkin"):
            raise Exception("Whoops!")

    scheduler().stop()

    assert_called_once(requests_mock)
    events = received_events(requests_mock)
    assert len(events) == 1
    assert_cron_event(events[0], "start")


def test_cron_logs_failure_to_send_event_when_status_code(mocker):
    mock_requests(mocker, status_code=500)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "error")

    cron = Cron("some-cron-checkin")
    cron.start()
    scheduler().stop()

    log_messages = received_messages(internal_logger_mock)
    assert len(log_messages) == 1
    assert (
        "Failed to transmit cron check-in `some-cron-checkin` start event"
        in log_messages[0]
    )
    assert ": 500 status code" in log_messages[0]


def test_cron_logs_failure_to_send_event_when_exception(mocker):
    mock_requests(mocker, raise_exception=True)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "error")

    cron = Cron("some-cron-checkin")
    cron.start()
    scheduler().stop()

    log_messages = received_messages(internal_logger_mock)
    assert len(log_messages) == 1
    assert (
        "Failed to transmit cron check-in `some-cron-checkin` start event"
        in log_messages[0]
    )
    assert ": Whoops!" in log_messages[0]


def test_deprecated_heartbeat_helper_behaves_like_cron_helper(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    def some_function():
        return "output"

    assert deprecated_heartbeat("some-cron-checkin", some_function) == "output"
    scheduler().stop()

    assert_called_times(requests_mock, 1)

    events = received_events(requests_mock)
    assert len(events) == 2
    assert_cron_event(events[0], "start")
    assert_cron_event(events[1], "finish")


def test_deprecated_heartbeat_helper_emits_deprecation_warning(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    deprecated_heartbeat("some-cron-checkin")

    for mock in [internal_logger_mock, print_mock]:
        messages = received_messages(mock)
        assert (
            len(
                [
                    message
                    for message in messages
                    if "The helper `heartbeat` has been deprecated" in message
                ]
            )
            == 1
        )


def test_deprecated_heartbeat_helper_only_emits_deprecation_warning_once(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    deprecated_heartbeat("some-heartbeat")
    deprecated_heartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        messages = received_messages(mock)
        assert (
            len(
                [
                    message
                    for message in messages
                    if "The helper `heartbeat` has been deprecated" in message
                ]
            )
            == 1
        )


def test_deprecated_heartbeat_class_returns_cron_instance():
    cron_instance = DeprecatedHeartbeat("some-heartbeat")
    assert isinstance(cron_instance, Cron)


def test_deprecated_heartbeat_instance_is_instance_of_cron_class():
    for instance_class in [Cron, DeprecatedHeartbeat]:
        for checked_class in [Cron, DeprecatedHeartbeat]:
            assert isinstance(instance_class("some-instance"), checked_class)


def test_deprecated_heartbeat_class_emits_deprecation_warning(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    DeprecatedHeartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        messages = received_messages(mock)
        assert (
            len(
                [
                    message
                    for message in messages
                    if "The class `Heartbeat` has been deprecated" in message
                ]
            )
            == 1
        )


def test_deprecated_heartbeat_class_only_emits_deprecation_warning_once(
    mocker, reset_heartbeat_warnings
):
    internal_logger_mock = mock_internal_logger(mocker, "warning")
    print_mock = mock_print(mocker)

    DeprecatedHeartbeat("some-heartbeat")
    DeprecatedHeartbeat("some-heartbeat")

    for mock in [internal_logger_mock, print_mock]:
        messages = received_messages(mock)
        assert (
            len(
                [
                    message
                    for message in messages
                    if "The class `Heartbeat` has been deprecated" in message
                ]
            )
            == 1
        )
