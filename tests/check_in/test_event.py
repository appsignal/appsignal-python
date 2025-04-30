import json
from itertools import permutations
from typing import cast

from appsignal.check_in.event import (
    Event,
    cron,
    deduplicate_cron,
    describe,
    heartbeat,
    is_redundant,
)


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


def test_deduplicate_cron_removes_redundant_pairs():
    first_start = cron("checkin-name", "first", "start")
    first_finish = cron("checkin-name", "first", "finish")
    second_start = cron("checkin-name", "second", "start")
    second_finish = cron("checkin-name", "second", "finish")
    base_events = [first_start, first_finish, second_start, second_finish]

    for events_tuple in permutations(base_events):
        events = list(events_tuple)  # Convert tuple to list for in-place modification
        deduplicate_cron(events)

        assert len(events) == 2
        assert events[0]["digest"] == events[1]["digest"]
        assert {"start", "finish"} == {events[0]["kind"], events[1]["kind"]}


def test_deduplicate_cron_keeps_unmatched_pairs():
    first_start = cron("checkin-name", "first", "start")
    second_start = cron("checkin-name", "second", "start")
    second_finish = cron("checkin-name", "second", "finish")
    third_finish = cron("checkin-name", "third", "finish")
    base_events = [first_start, second_start, second_finish, third_finish]

    for events_tuple in permutations(base_events):
        events = list(events_tuple)  # Convert tuple to list for in-place modification
        deduplicate_cron(events)

        assert len(events) == 4
        for event in [first_start, second_start, second_finish, third_finish]:
            assert event in events


def test_deduplicate_cron_keeps_different_identifiers():
    first_start = cron("checkin-name", "first", "start")
    first_finish = cron("checkin-name", "first", "finish")
    second_start = cron("other-name", "second", "start")
    second_finish = cron("other-name", "second", "finish")
    base_events = [first_start, first_finish, second_start, second_finish]

    for events_tuple in permutations(base_events):
        events = list(events_tuple)  # Convert tuple to list for in-place modification
        deduplicate_cron(events)

        assert len(events) == 4
        for event in [first_start, first_finish, second_start, second_finish]:
            assert event in events
