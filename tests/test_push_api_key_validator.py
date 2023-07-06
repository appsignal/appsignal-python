from appsignal.push_api_key_validator import PushApiKeyValidator
from appsignal.config import Config, Options
from unittest.mock import MagicMock

def test_push_api_key_validator_valid(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=200)

    assert PushApiKeyValidator.validate(Config(Options(push_api_key='valid'))) == 'valid'

def test_push_api_key_validator_invalid(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=401)

    assert PushApiKeyValidator.validate(Config(Options(push_api_key='invalid'))) == 'invalid'

def test_push_api_key_validator_error(mocker):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=500)

    assert PushApiKeyValidator.validate(Config(Options(push_api_key='500'))) == 500
