import json
from typing import cast

from appsignal.check_in.event import Event, cron, describe, heartbeat, is_redundant


def test_describe_no_events():
    assert describe([]) == "no check-in events"


def test_describe_heartbeat_event():
    events = [heartbeat("some-event")]
    assert describe(events) == "heartbeat check-in `some-event` event"


def test_describe_cron_event():
    events = [cron("some-event", "abc", "start")]
    assert describe(events) == "cron check-in `some-event` start event (digest abc)"


def test_describe_multiple_events():
    events = [heartbeat("event"), cron("some-event", "abc", "start")]
    assert describe(events) == "2 check-in events"


def test_describe_unknown_event():
    event = cast(Event, {"check_in_type": "unknown"})
    assert describe([event]) == "unknown check-in event"


def test_is_redundant_heartbeat_with_same_name():
    event = heartbeat("some-event")
    redundant = heartbeat("some-event")
    assert is_redundant(event, redundant)


def test_is_redundant_heartbeat_with_different_name():
    event = heartbeat("some-event")
    redundant = heartbeat("other-event")
    assert not is_redundant(event, redundant)


def test_is_redundant_heartbeat_and_cron():
    event = heartbeat("some-event")
    redundant = cron("some-event", "abc", "start")
    assert not is_redundant(event, redundant)


def test_is_redundant_cron_with_same_name_digest_and_kind():
    event = cron("some-event", "abc", "start")
    redundant = cron("some-event", "abc", "start")
    assert is_redundant(event, redundant)


def test_is_redundant_cron_with_same_name_and_digest_but_different_kind():
    event = cron("some-event", "abc", "start")
    redundant = cron("some-event", "abc", "finish")
    assert not is_redundant(event, redundant)


def test_is_redundant_cron_with_same_name_and_kind_but_different_digest():
    event = cron("some-event", "abc", "start")
    redundant = cron("some-event", "def", "start")
    assert not is_redundant(event, redundant)


def test_is_redundant_cron_with_same_digest_and_kind_but_different_name():
    event = cron("some-event", "abc", "start")
    redundant = cron("other-event", "abc", "start")
    assert not is_redundant(event, redundant)


def test_is_redundant_unknown_event():
    event = cast(Event, {"check_in_type": "unknown"})
    assert not is_redundant(event, event)


def test_cron_event_json_serialised():
    event = cron("some-event", "abc", "start")
    serialised = json.dumps(event)
    assert '"check_in_type": "cron"' in serialised
    assert '"kind": "start"' in serialised
    assert '"digest": "abc"' in serialised
    assert '"identifier": "some-event"' in serialised
    assert '"timestamp":' in serialised


def test_heartbeat_event_json_serialised():
    event = heartbeat("some-event")
    serialised = json.dumps(event)
    assert '"check_in_type": "heartbeat"' in serialised
    assert '"identifier": "some-event"' in serialised
    assert '"timestamp":' in serialised
    assert '"kind":' not in serialised
    assert '"digest":' not in serialised
