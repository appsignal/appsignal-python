from appsignal.check_in.event import heartbeat
from appsignal.check_in.scheduler import Scheduler, scheduler

from ..utils import wait_until
from .utils import (
    assert_called_once,
    assert_called_times,
    assert_url_config,
    init_client,
    mock_internal_logger,
    mock_requests,
    received_events,
    received_messages,
    received_url,
)


def test_scheduler_transmits_scheduled_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "debug")

    scheduler().schedule(heartbeat("event"))
    assert not requests_mock.called

    wait_until(
        lambda: scheduler()._transmitted == 1,
        "the scheduler did not transmit the event",
    )

    assert_called_once(requests_mock)
    assert_url_config(received_url(requests_mock))

    events = received_events(requests_mock)
    assert len(events) == 1
    assert events[0]["identifier"] == "event"

    log_messages = received_messages(internal_logger_mock)
    assert len(log_messages) == 2
    assert (
        log_messages[0]
        == "Scheduling heartbeat check-in `event` event to be transmitted"
    )
    assert log_messages[1] == "Transmitted heartbeat check-in `event` event"


def test_scheduler_debounces_events_scheduled_quickly(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "debug")

    scheduler().schedule(heartbeat("first"))
    scheduler().schedule(heartbeat("second"))
    assert not requests_mock.called

    wait_until(
        lambda: scheduler()._transmitted == 1,
        "the scheduler did not transmit the events",
    )

    assert_called_once(requests_mock)
    assert_url_config(received_url(requests_mock))

    events = received_events(requests_mock)
    assert len(events) == 2
    assert events[0]["identifier"] == "first"
    assert events[1]["identifier"] == "second"

    log_messages = received_messages(internal_logger_mock)
    assert len(log_messages) == 3
    assert (
        log_messages[0]
        == "Scheduling heartbeat check-in `first` event to be transmitted"
    )
    assert (
        log_messages[1]
        == "Scheduling heartbeat check-in `second` event to be transmitted"
    )
    assert log_messages[2] == "Transmitted 2 check-in events"


def test_scheduler_sends_events_scheduled_slowly_separately(mocker):
    requests_mock = mock_requests(mocker)
    init_client()
    Scheduler.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS = 0.1

    scheduler().schedule(heartbeat("first"))
    wait_until(
        lambda: scheduler()._transmitted == 1,
        "the scheduler did not transmit the first event",
    )
    scheduler().schedule(heartbeat("second"))
    wait_until(
        lambda: scheduler()._transmitted == 2,
        "the scheduler did not transmit the second event",
    )

    assert_called_times(requests_mock, 2)

    first_events = received_events(requests_mock, call=0)
    assert len(first_events) == 1
    assert first_events[0]["identifier"] == "first"

    second_events = received_events(requests_mock, call=1)
    assert len(second_events) == 1
    assert second_events[0]["identifier"] == "second"


def test_scheduler_sends_events_scheduled_immediately_on_stop(mocker):
    # Set all debounce intervals to 10 seconds, to make the test
    # fail if it waits for the debounce -- this ensures that what is being
    # tested is that the events are transmitted immediately when the
    # scheduler is stopped, without waiting for any debounce.

    requests_mock = mock_requests(mocker)
    init_client()
    Scheduler.INITIAL_DEBOUNCE_SECONDS = 10
    Scheduler.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS = 10

    scheduler().schedule(heartbeat("first"))
    scheduler().stop()
    wait_until(
        lambda: scheduler()._transmitted == 1,
        "the scheduler did not transmit the event",
    )

    assert_called_once(requests_mock)

    events = received_events(requests_mock)
    assert len(events) == 1
    assert events[0]["identifier"] == "first"


def test_scheduler_does_not_transmit_when_stopped(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    internal_logger_mock = mock_internal_logger(mocker, "debug")

    scheduler().stop()
    scheduler().schedule(heartbeat("some-heartbeat-checkin"))

    assert not requests_mock.called

    log_messages = received_messages(internal_logger_mock)
    assert len(log_messages) == 1
    assert log_messages[0] == (
        "Cannot transmit heartbeat check-in `some-heartbeat-checkin` event: "
        "AppSignal is stopped"
    )
