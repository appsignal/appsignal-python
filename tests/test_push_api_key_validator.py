from unittest.mock import MagicMock

from appsignal.config import Config, Options
from appsignal.push_api_key_validator import PushApiKeyValidator


config = Config(
    Options(
        push_api_key="some-push-api-key",
        name="some-app",
        environment="staging",
        hostname="beepboop.local",
    )
)


def test_push_api_key_validator_valid(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=200)

    assert PushApiKeyValidator.validate(config) == "valid"
    assert mock_request.called

    assert "https://push.appsignal.com/1/auth?" in mock_request.call_args[0][0]
    # The ordering of query parameters is not guaranteed.
    assert "api_key=some-push-api-key" in mock_request.call_args[0][0]
    assert "environment=staging" in mock_request.call_args[0][0]
    assert "hostname=beepboop.local" in mock_request.call_args[0][0]
    assert "name=some-app" in mock_request.call_args[0][0]


def test_push_api_key_validator_invalid(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=401)

    assert PushApiKeyValidator.validate(config) == "invalid"
    assert mock_request.called


def test_push_api_key_validator_error(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=500)

    assert PushApiKeyValidator.validate(config) == "500"
    assert mock_request.called
