import requests

from appsignal.config import Config


class PushApiKeyValidator:
    @staticmethod
    def validate(config: Config):
        endpoint = config.option("endpoint")
        url = f"{endpoint}/1/auth?api_key={config.option('push_api_key')}"
        proxies = {}
        if config.option("http_proxy"):
            proxies["http"] = config.option("http_proxy")
            proxies["https"] = config.option("http_proxy")

        cert = config.option("ca_file_path")
        response = requests.post(url, proxies=proxies, verify=cert)

        if response.status_code == 200:
            return "valid"
        elif response.status_code == 401:
            return "invalid"
        else:
            return response.status_code
