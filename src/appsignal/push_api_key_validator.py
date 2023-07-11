import urllib

import requests

from appsignal.config import Config


class PushApiKeyValidator:
    @staticmethod
    def validate(config: Config) -> str:
        endpoint = config.option("endpoint")
        params = urllib.parse.urlencode(
            {
                "api_key": config.option("push_api_key"),
                "name": config.option("name"),
                "environment": config.option("environment"),
                "hostname": config.option("hostname") or "",
            }
        )

        url = f"{endpoint}/1/auth?{params}"
        proxies = {}
        if config.option("http_proxy"):
            proxies["http"] = config.option("http_proxy")
            proxies["https"] = config.option("http_proxy")

        cert = config.option("ca_file_path")
        response = requests.post(url, proxies=proxies, verify=cert)

        if response.status_code == 200:
            return "valid"
        if response.status_code == 401:
            return "invalid"
        return str(response.status_code)
