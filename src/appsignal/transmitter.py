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
    proxy = config.proxy_for(url)
    if proxy:
        proxies["http"] = proxy
        proxies["https"] = proxy

    cert = config.option("ca_file_path")

    # A `requests` session that reads the environment adds the proxies it
    # finds there, so it must not read them.
    with requests.Session() as session:
        session.trust_env = False

        if ndjson is not None:
            data = ndjson_dumps(ndjson)
            headers = {"Content-Type": "application/x-ndjson"}
            return session.post(
                url, data=data, headers=headers, proxies=proxies, verify=cert
            )

        return session.post(url, json=json, proxies=proxies, verify=cert)
