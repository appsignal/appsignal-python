from __future__ import annotations

import os
from runpy import run_path

from .client import Client as Appsignal
from .heartbeat import Heartbeat, heartbeat
from .metrics import add_distribution_value, increment_counter, set_gauge
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
    "add_distribution_value",
    "Heartbeat",
    "heartbeat",
    "start",
]


# Load the AppSignal client from the app specific `__appsignal__.py` client
# file. This loads the user config, rather than our default config.
# If no client file is found it return `None`.
# If there's a problem with the client file it will raise an
# `InvalidClientFileError` with a message containing more details.
def _client_from_config_file() -> Appsignal | None:
    cwd = os.getcwd()
    app_config_path = os.path.join(cwd, "__appsignal__.py")
    if os.path.exists(app_config_path):
        try:
            client = run_path(app_config_path)["appsignal"]
            if not isinstance(client, Appsignal):
                raise InvalidClientFileError(
                    "The `appsignal` variable in `__appsignal__.py` does not "
                    "contain an AppSignal client. "
                    "Please define the configuration file as described in "
                    "our documentation: "
                    "https://docs.appsignal.com/python/configuration.html"
                )

            return client
        except KeyError as error:
            raise InvalidClientFileError(
                "No `appsignal` variable found in `__appsignal__.py`. "
                "Please define the configuration file as described in "
                "our documentation: "
                "https://docs.appsignal.com/python/configuration.html"
            ) from error

    return None


def _must_client_from_config_file() -> Appsignal:
    client = _client_from_config_file()
    if client is None:
        raise InvalidClientFileError(
            "No `__appsignal__.py` file found in the current directory. "
            "Please define the configuration file as described in "
            "our documentation: "
            "https://docs.appsignal.com/python/configuration.html"
        )

    return client


def start() -> None:
    _must_client_from_config_file().start()


class InvalidClientFileError(Exception):
    pass


# Try and load the appsignal-beta package. If it's present and imported, it
# will print a message about switching to the `appsignal` package.
try:
    import appsignal_beta  # type:ignore # noqa: F401
except ImportError:
    pass
