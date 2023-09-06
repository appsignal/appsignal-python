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


def test_set_attributes(mocker):
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


def test_set_error(mocker):
    with tracer.start_as_current_span("current span name") as current_span:
        current_set_status_spy = mocker.spy(current_span, "set_status")
        current_record_exception_spy = mocker.spy(current_span, "record_exception")

        error = Exception("Whoops!")

        set_error(error)

        current_set_status_spy.assert_called_once()
        assert current_set_status_spy.call_args.args[0].status_code == StatusCode.ERROR
        current_record_exception_spy.assert_called_with(error)


def test_set_error_on_span(mocker):
    with tracer.start_as_current_span("other span name") as other_span:
        other_set_status_spy = mocker.spy(other_span, "set_status")
        other_record_exception_spy = mocker.spy(other_span, "record_exception")

        with tracer.start_as_current_span("current span name") as current_span:
            current_set_status_spy = mocker.spy(current_span, "set_status")
            current_record_exception_spy = mocker.spy(current_span, "record_exception")

            error = Exception("Whoops!")

            set_error(error, other_span)

            other_set_status_spy.assert_called_once()
            assert (
                other_set_status_spy.call_args.args[0].status_code == StatusCode.ERROR
            )
            other_record_exception_spy.assert_called_once_with(error)

            current_set_status_spy.assert_not_called()
            current_record_exception_spy.assert_not_called()


def test_send_error(mocker):
    class FooError(Exception):
        pass

    error = FooError("Whoops!")

    span_mock = mocker.Mock()
    span_mock.set_status = mocker.Mock()
    span_mock.record_exception = mocker.Mock()
    context_manager_mock = mocker.Mock()
    context_manager_mock.__enter__ = mocker.Mock(return_value=span_mock)
    context_manager_mock.__exit__ = mocker.Mock()
    start_as_current_span_mock = mocker.Mock(return_value=context_manager_mock)

    mocker.patch(
        "appsignal.helpers._send_error_tracer.start_as_current_span",
        new=start_as_current_span_mock,
    )

    send_error(error)

    start_as_current_span_mock.assert_called_once_with("FooError")
    assert span_mock.set_status.call_args.args[0].status_code == StatusCode.ERROR
    span_mock.record_exception.assert_called_once_with(error)


def test_send_error_with_context(mocker):
    class FooError(Exception):
        pass

    error = FooError("Whoops!")

    span_mock = mocker.Mock()
    span_mock.set_status = mocker.Mock()
    span_mock.record_exception = mocker.Mock()
    span_mock.set_attribute = mocker.Mock()
    context_manager_mock = mocker.Mock()
    context_manager_mock.__enter__ = mocker.Mock(return_value=span_mock)
    context_manager_mock.__exit__ = mocker.Mock()
    start_as_current_span_mock = mocker.Mock(return_value=context_manager_mock)

    mocker.patch(
        "appsignal.helpers._send_error_tracer.start_as_current_span",
        new=start_as_current_span_mock,
    )

    with send_error_with_context(error) as span:
        set_params({"foo": "bar"}, span)

    start_as_current_span_mock.assert_called_once_with("FooError")
    assert span_mock.set_status.call_args.args[0].status_code == StatusCode.ERROR
    span_mock.record_exception.assert_called_once_with(error)
    span_mock.set_attribute.assert_called_once_with(
        "appsignal.request.parameters", '{"foo": "bar"}'
    )
