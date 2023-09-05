from .client import Client as Appsignal
from .helpers import (
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


__all__ = [
    "Appsignal",
    "set_body",
    "set_category",
    "set_custom_data",
    "set_header",
    "set_name",
    "set_namespace",
    "set_params",
    "set_root_name",
    "set_session_data",
    "set_tag",
]


# Try and load the appsignal-beta package. If it's present and imported, it
# will print a message about switching to the `appsignal` package.
try:
    import appsignal_beta  # type:ignore # noqa: F401
except ImportError:
    pass
