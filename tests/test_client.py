from appsignal.client import Client

import os


def test_client_options_merge_sources():
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some_key"
    client = Client(name="MyApp")
    assert client._options["name"] == "MyApp"
    assert client._options["push_api_key"] == "some_key"
    assert "app_path" in client._options


def test_client_active():
    client = Client(active=True, name="MyApp")
    assert client._options["active"] is True
    assert client._options["name"] == "MyApp"
    client.start()

    # Sets the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") == "true"
    assert os.environ.get("_APPSIGNAL_APP_NAME") == "MyApp"


def test_client_inactive():
    client = Client(active=False, name="MyApp")
    assert client._options["active"] is False
    assert client._options["name"] == "MyApp"
    client.start()

    # Does not set the private config environment variables
    assert os.environ.get("_APPSIGNAL_ACTIVE") is None
    assert os.environ.get("_APPSIGNAL_APP_NAME") is None
