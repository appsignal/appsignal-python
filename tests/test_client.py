from appsignal.client import Client

import os


def test_client_options_merge_init_with_env():
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some_key"
    client = Client(name="MyApp")
    assert client._options["name"] == "MyApp"
    assert client._options["push_api_key"] == "some_key"
