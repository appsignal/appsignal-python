from __future__ import annotations

import urllib
from typing import TYPE_CHECKING, Any

import requests

from appsignal.client import Client
from appsignal.config import Config


if TYPE_CHECKING:
    from requests import Response


def transmit(
    url: str, json: Any | None = None, config: Config | None = None
) -> Response:
    if config is None:
        config = Client.config() or Config()

    params = urllib.parse.urlencode(
        {
            "api_key": config.option("push_api_key") or "",
            "name": config.option("name") or "",
            "environment": config.option("environment") or "",
            "hostname": config.option("hostname") or "",
        }
    )

    url = f"{url}?{params}"

    proxies = {}
    if config.option("http_proxy"):
        proxies["http"] = config.option("http_proxy")
        proxies["https"] = config.option("http_proxy")

    cert = config.option("ca_file_path")

    return requests.post(url, json=json, proxies=proxies, verify=cert)
