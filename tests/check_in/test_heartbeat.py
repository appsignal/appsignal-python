from appsignal.check_in import heartbeat
from appsignal.check_in.heartbeat import _set_heartbeat_continuous_interval_seconds
from appsignal.check_in.scheduler import Scheduler, scheduler

from ..utils import wait_until
from .utils import (
    assert_called_at_least,
    assert_called_once,
    assert_url_config,
    init_client,
    mock_requests,
    received_events,
    received_url,
)


def assert_heartbeat_event(event):
    assert event["identifier"] == "some-heartbeat"
    assert "kind" not in event
    assert "digest" not in event
    assert isinstance(event["timestamp"], int)
    assert event["check_in_type"] == "heartbeat"


def test_heartbeat_sends_heartbeat_event(mocker):
    requests_mock = mock_requests(mocker)
    init_client()

    heartbeat("some-heartbeat")
    scheduler().stop()

    assert_called_once(requests_mock)

    assert_url_config(received_url(requests_mock))

    events = received_events(requests_mock)
    assert len(events) == 1
    assert_heartbeat_event(events[0])


def test_heartbeat_continuous_sends_heartbeat_events_forever(mocker):
    _set_heartbeat_continuous_interval_seconds(0.05)
    Scheduler.BETWEEN_TRANSMISSIONS_DEBOUNCE_SECONDS = 0.1

    requests_mock = mock_requests(mocker)
    init_client()

    heartbeat("some-heartbeat", continuous=True)
    wait_until(
        lambda: scheduler()._transmitted >= 2,
        "the scheduler did not transmit two events",
    )

    assert_called_at_least(requests_mock, 2)

    for call in [0, 1]:
        events = received_events(requests_mock, call=call)
        assert len(events) == 1
        assert_heartbeat_event(events[0])
