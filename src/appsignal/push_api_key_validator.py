from appsignal.config import Config
from appsignal.transmitter import transmit


class PushApiKeyValidator:
    @staticmethod
    def validate(config: Config) -> str:
        endpoint = config.option("endpoint")
        url = f"{endpoint}/1/auth"

        response = transmit(url, config=config)

        if response.status_code == 200:
            return "valid"
        if response.status_code == 401:
            return "invalid"
        return str(response.status_code)
