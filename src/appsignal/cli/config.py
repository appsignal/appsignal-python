from __future__ import annotations

import os
from runpy import run_path

from ..client import Client


# Load the AppSignal client from the app specific `__appsignal__.py` client
# file. This loads the user config, rather than our default config.
# If no client file is found it return `None`.
# If there's a problem with the client file it will raise an
# `InvalidClientFileError` with a message containing more details.
def _client_from_config_file() -> Client | None:
    cwd = os.getcwd()
    app_config_path = os.path.join(cwd, "__appsignal__.py")
    if os.path.exists(app_config_path):
        try:
            client = run_path(app_config_path)["appsignal"]
            if not isinstance(client, Client):
                raise InvalidClientFileError(
                    "The `appsignal` variable does not contain an AppSignal client. "
                    "Please define the configuration file as described in "
                    "our documentation: "
                    "https://docs.appsignal.com/python/configuration.html"
                )

            return client
        except KeyError as error:
            raise InvalidClientFileError(
                "No `appsignal` variable found. "
                "Please define the configuration file as described in "
                "our documentation: "
                "https://docs.appsignal.com/python/configuration.html"
            ) from error

    return None


class InvalidClientFileError(Exception):
    pass
