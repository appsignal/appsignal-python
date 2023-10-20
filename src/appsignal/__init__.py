from .client import Client as Appsignal
from .metrics import increment_counter, set_gauge
from .tracing import (
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
    set_sql_body,
    set_tag,
)


__all__ = [
    "Appsignal",
    "set_body",
    "set_sql_body",
    "set_category",
    "set_custom_data",
    "set_header",
    "set_name",
    "set_namespace",
    "set_params",
    "set_root_name",
    "set_session_data",
    "set_tag",
    "set_error",
    "send_error",
    "send_error_with_context",
    "increment_counter",
    "set_gauge",
]


# Try and load the appsignal-beta package. If it's present and imported, it
# will print a message about switching to the `appsignal` package.
try:
    import appsignal_beta  # type:ignore # noqa: F401
except ImportError:
    pass
