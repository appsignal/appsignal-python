from __future__ import annotations

from opentelemetry import trace

from appsignal import (
    set_body,
    set_category,
    set_custom_data,
    set_header,
    set_name,
    set_namespace,
    set_params,
    set_root_name,
    set_session_data,
    set_tag,
)


def test_set_attributes(mocker):
    tracer = trace.get_tracer("appsignal")
    with tracer.start_as_current_span("current span name") as current_span:
        current_spy = mocker.spy(current_span, "set_attribute")

        set_body("SELECT * FROM users")
        current_spy.assert_called_with("appsignal.body", "SELECT * FROM users")

        set_category("some.query")
        current_spy.assert_called_with("appsignal.category", "some.query")

        set_name("Some query")
        current_spy.assert_called_with("appsignal.name", "Some query")

        set_custom_data({"chunky": "bacon"})
        current_spy.assert_called_with("appsignal.custom_data", '{"chunky": "bacon"}')

        set_params({"id": 123})
        current_spy.assert_called_with("appsignal.request.parameters", '{"id": 123}')

        set_session_data({"admin": True})
        current_spy.assert_called_with(
            "appsignal.request.session_data", '{"admin": true}'
        )

        set_header("content-type", "application/json")
        current_spy.assert_called_with(
            "appsignal.request.headers.content-type", "application/json"
        )

        set_tag("something", True)
        current_spy.assert_called_with("appsignal.tag.something", True)

        set_namespace("web")
        current_spy.assert_called_with("appsignal.namespace", "web")

        set_root_name("Root name")
        current_spy.assert_called_with("appsignal.root_name", "Root name")


def test_set_attributes_on_span(mocker):
    tracer = trace.get_tracer("appsignal")
    with tracer.start_as_current_span("other span name") as other_span:
        other_spy = mocker.spy(other_span, "set_attribute")

        with tracer.start_as_current_span("current span name") as current_span:
            current_spy = mocker.spy(current_span, "set_attribute")

            set_body("SELECT * FROM users", other_span)
            other_spy.assert_called_with("appsignal.body", "SELECT * FROM users")

            set_category("some.query", other_span)
            other_spy.assert_called_with("appsignal.category", "some.query")

            set_name("Some query", other_span)
            other_spy.assert_called_with("appsignal.name", "Some query")

            set_custom_data({"chunky": "bacon"}, other_span)
            other_spy.assert_called_with("appsignal.custom_data", '{"chunky": "bacon"}')

            set_params({"id": 123}, other_span)
            other_spy.assert_called_with("appsignal.request.parameters", '{"id": 123}')

            set_session_data({"admin": True}, other_span)
            other_spy.assert_called_with(
                "appsignal.request.session_data", '{"admin": true}'
            )

            set_header("content-type", "application/json", other_span)
            other_spy.assert_called_with(
                "appsignal.request.headers.content-type", "application/json"
            )

            set_tag("something", True, other_span)
            other_spy.assert_called_with("appsignal.tag.something", True)

            set_namespace("web", other_span)
            other_spy.assert_called_with("appsignal.namespace", "web")

            set_root_name("Root name", other_span)
            other_spy.assert_called_with("appsignal.root_name", "Root name")

            current_spy.assert_not_called()
