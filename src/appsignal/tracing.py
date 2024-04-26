from __future__ import annotations

import json
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.trace import Status, StatusCode

from . import internal_logger as logger


if TYPE_CHECKING:
    from opentelemetry.trace import Span


def _set_attribute(attribute: str, value: Any, span: Span | None = None) -> None:
    span = span or trace.get_current_span()

    if span is trace.INVALID_SPAN:
        attribute_suffix = attribute.split(".")[-1]
        logger.debug(f"There is no active span, cannot set `{attribute_suffix}`")
        return

    span.set_attribute(attribute, value)


def _set_serialised_attribute(
    attribute: str, value: Any, span: Span | None = None
) -> None:
    try:
        serialised_value = json.dumps(value)
        _set_attribute(attribute, serialised_value, span)
    except (TypeError, ValueError) as error:
        attribute_suffix = attribute.split(".")[-1]
        logger.info(f"Failed to serialise attribute `{attribute_suffix}`: {error}")


def _set_prefixed_attribute(
    prefix: str, suffix: str, value: Any, span: Span | None = None
) -> None:
    if suffix:
        _set_attribute(f"{prefix}.{suffix}", value, span)


def set_params(params: Any, span: Span | None = None) -> None:
    _set_serialised_attribute("appsignal.request.parameters", params, span)


def set_session_data(session_data: Any, span: Span | None = None) -> None:
    _set_serialised_attribute("appsignal.request.session_data", session_data, span)


def set_custom_data(custom_data: Any, span: Span | None = None) -> None:
    _set_serialised_attribute("appsignal.custom_data", custom_data, span)


def set_tag(tag: str, value: Any, span: Span | None = None) -> None:
    _set_prefixed_attribute("appsignal.tag", tag, value, span)


def set_header(header: str, value: Any, span: Span | None = None) -> None:
    _set_prefixed_attribute("appsignal.request.headers", header, value, span)


def set_name(name: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.name", name, span)


def set_category(category: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.category", category, span)


def set_body(body: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.body", body, span)


def set_sql_body(body: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.sql_body", body, span)


def set_namespace(namespace: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.namespace", namespace, span)


def set_root_name(root_name: str, span: Span | None = None) -> None:
    _set_attribute("appsignal.root_name", root_name, span)


def set_error(error: Exception, span: Span | None = None) -> None:
    span = span or trace.get_current_span()
    span.set_status(Status(StatusCode.ERROR))
    span.record_exception(error)


def send_error(error: Exception) -> None:
    with send_error_with_context(error):
        pass


_send_error_tracer = trace.get_tracer("Appsignal.send_error")


@contextmanager
def send_error_with_context(error: Exception) -> Iterator[Span]:
    name = error.__class__.__name__

    # Passing an empty context ensures the new span does not use the current
    # global context, meaning it will be the root span of a new trace, not a
    # child of the current span and trace in the global context:
    with _send_error_tracer.start_as_current_span(name, context=Context()) as span:
        set_error(error, span)
        yield span
