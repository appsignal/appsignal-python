from __future__ import annotations

import urllib
from typing import TYPE_CHECKING, Any

import requests

from .client import Client
from .config import Config
from .ndjson import dumps as ndjson_dumps


if TYPE_CHECKING:
    from requests import Response


def transmit(
    url: str,
    json: Any | None = None,
    ndjson: list[Any] | None = None,
    config: Config | None = None,
) -> Response:
    if config is None:
        config = Client.config() or Config()

    if json is not None and ndjson is not None:
        raise ValueError("Cannot send both `json` and `ndjson`")

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

    if ndjson is not None:
        data = ndjson_dumps(ndjson)
        headers = {"Content-Type": "application/x-ndjson"}
        return requests.post(
            url, data=data, headers=headers, proxies=proxies, verify=cert
        )

    return requests.post(url, json=json, proxies=proxies, verify=cert)
