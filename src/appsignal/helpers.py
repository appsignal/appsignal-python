from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


if TYPE_CHECKING:
    from opentelemetry.trace import Span

logger = logging.getLogger("appsignal")


def set_attribute(attribute: str, value: Any, span: Span | None = None) -> None:
    span = span or trace.get_current_span()
    # TODO: `trace.get_current_span` will return an INVALID_SPAN
    # if there is no current span. Should we log something about
    # it? The Node.js integration does log something about it.
    #
    # To detect if it's an invalid span, it seems we would have
    # to do something like:
    # `span.get_span_context().is_valid`
    span.set_attribute(attribute, value)


def set_serialised_attribute(
    attribute: str, value: Any, span: Span | None = None
) -> None:
    serialised_value = json.dumps(value)
    set_attribute(attribute, serialised_value, span)


def set_prefixed_attribute(
    prefix: str, suffix: str, value: Any, span: Span | None = None
) -> None:
    if suffix:
        set_attribute(f"{prefix}.{suffix}", value, span)


def set_params(params: Any, span: Span | None = None) -> None:
    set_serialised_attribute("appsignal.request.parameters", params, span)


def set_session_data(session_data: Any, span: Span | None = None) -> None:
    set_serialised_attribute("appsignal.request.session_data", session_data, span)


def set_custom_data(custom_data: Any, span: Span | None = None) -> None:
    set_serialised_attribute("appsignal.custom_data", custom_data, span)


def set_tag(tag: str, value: Any, span: Span | None = None) -> None:
    set_prefixed_attribute("appsignal.tag", tag, value, span)


def set_header(header: str, value: Any, span: Span | None = None) -> None:
    set_prefixed_attribute("appsignal.request.headers", header, value, span)


def set_name(name: str, span: Span | None = None) -> None:
    set_attribute("appsignal.name", name, span)


def set_category(category: str, span: Span | None = None) -> None:
    set_attribute("appsignal.category", category, span)


def set_body(body: str, span: Span | None = None) -> None:
    set_attribute("appsignal.body", body, span)


def set_namespace(namespace: str, span: Span | None = None) -> None:
    set_attribute("appsignal.namespace", namespace, span)


def set_root_name(root_name: str, span: Span | None = None) -> None:
    set_attribute("appsignal.root_name", root_name, span)


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

    # TODO: this needs to always be a root span somehow!!!!
    with _send_error_tracer.start_as_current_span(name) as span:
        set_error(error, span)
        yield span
