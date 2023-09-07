from __future__ import annotations

from opentelemetry import trace
from opentelemetry.trace import StatusCode

from appsignal import (
    send_error,
    send_error_with_context,
    set_body,
    set_category,
    set_custom_data,
    set_error,
    set_header,
    set_name,
    set_namespace,
    set_params,
    set_root_name,
    set_session_data,
    set_tag,
)


tracer = trace.get_tracer("appsignal/tests")


class FooError(Exception):
    pass


def raised_error():
    try:
        raise FooError("Whoops!")
    except FooError as error:
        return error


def test_set_attributes(spans):
    with tracer.start_as_current_span("span"):
        set_body("SELECT * FROM users")
        set_category("some.query")
        set_name("Some query")
        set_custom_data({"chunky": "bacon"})
        set_params({"id": 123})
        set_session_data({"admin": True})
        set_header("content-type", "application/json")
        set_tag("something", True)
        set_namespace("web")
        set_root_name("Root name")

    assert dict(spans()[0].attributes) == {
        "appsignal.body": "SELECT * FROM users",
        "appsignal.category": "some.query",
        "appsignal.name": "Some query",
        "appsignal.custom_data": '{"chunky": "bacon"}',
        "appsignal.request.parameters": '{"id": 123}',
        "appsignal.request.session_data": '{"admin": true}',
        "appsignal.request.headers.content-type": "application/json",
        "appsignal.tag.something": True,
        "appsignal.namespace": "web",
        "appsignal.root_name": "Root name",
    }


def test_set_attributes_on_span(spans):
    with tracer.start_as_current_span("parent span") as span:
        with tracer.start_as_current_span("child span"):
            set_body("SELECT * FROM users", span)
            set_category("some.query", span)
            set_name("Some query", span)
            set_custom_data({"chunky": "bacon"}, span)
            set_params({"id": 123}, span)
            set_session_data({"admin": True}, span)
            set_header("content-type", "application/json", span)
            set_tag("something", True, span)
            set_namespace("web", span)
            set_root_name("Root name", span)

    spans = spans()
    assert len(spans) == 2

    parent_span = next(span for span in spans if span.name == "parent span")
    assert dict(parent_span.attributes) == {
        "appsignal.body": "SELECT * FROM users",
        "appsignal.category": "some.query",
        "appsignal.name": "Some query",
        "appsignal.custom_data": '{"chunky": "bacon"}',
        "appsignal.request.parameters": '{"id": 123}',
        "appsignal.request.session_data": '{"admin": true}',
        "appsignal.request.headers.content-type": "application/json",
        "appsignal.tag.something": True,
        "appsignal.namespace": "web",
        "appsignal.root_name": "Root name",
    }

    child_span = next(span for span in spans if span.name == "child span")
    assert dict(child_span.attributes) == {}


def test_set_error(spans):
    with tracer.start_as_current_span("current span name"):
        set_error(raised_error())

    span = spans()[0]
    assert span.status.status_code == StatusCode.ERROR
    event = span.events[0]
    assert event.name == "exception"
    assert event.attributes["exception.type"] == "FooError"
    assert event.attributes["exception.message"] == "Whoops!"


def test_set_error_on_span(spans):
    with tracer.start_as_current_span("parent span") as span:
        with tracer.start_as_current_span("child span"):
            set_error(raised_error(), span)

    spans = spans()
    assert len(spans) == 2

    parent_span = next(span for span in spans if span.name == "parent span")
    assert parent_span.status.status_code == StatusCode.ERROR

    event = parent_span.events[0]
    assert event.name == "exception"
    assert event.attributes["exception.type"] == "FooError"
    assert event.attributes["exception.message"] == "Whoops!"

    child_span = next(span for span in spans if span.name == "child span")
    assert len(child_span.events) == 0


def test_send_error(spans):
    send_error(raised_error())

    span = spans()[0]
    assert span.name == "FooError"
    assert span.status.status_code == StatusCode.ERROR

    event = span.events[0]
    assert event.name == "exception"
    assert event.attributes["exception.type"] == "FooError"
    assert event.attributes["exception.message"] == "Whoops!"


def test_send_error_with_current_span(spans):
    with tracer.start_as_current_span("current span"):
        send_error(raised_error())

    spans = spans()
    assert len(spans) == 2

    current_span = next(span for span in spans if span.name == "current span")
    assert current_span.status.status_code != StatusCode.ERROR
    assert len(current_span.events) == 0

    error_span = next(span for span in spans if span.name == "FooError")
    assert error_span.status.status_code == StatusCode.ERROR

    event = error_span.events[0]
    assert event.name == "exception"
    assert event.attributes["exception.type"] == "FooError"
    assert event.attributes["exception.message"] == "Whoops!"

    assert current_span.parent is None
    assert (
        current_span.get_span_context().trace_id
        != error_span.get_span_context().trace_id
    )


def test_send_error_with_context(spans):
    # Using implicit current span
    with send_error_with_context(raised_error()):
        set_params({"foo": "bar"})

    # Using explicit `with` block span
    with send_error_with_context(raised_error()) as current_span:
        set_params({"foo": "bar"}, current_span)

    spans = spans()
    assert len(spans) == 2

    for span in spans:
        assert span.name == "FooError"
        assert span.status.status_code == StatusCode.ERROR
        assert dict(span.attributes) == {
            "appsignal.request.parameters": '{"foo": "bar"}'
        }

        event = span.events[0]
        assert event.name == "exception"
        assert event.attributes["exception.type"] == "FooError"
        assert event.attributes["exception.message"] == "Whoops!"
