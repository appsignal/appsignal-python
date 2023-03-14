from appsignal.client import Client


def test_client_init():
    client = Client(name="MyApp")
    assert client._options["name"] == "MyApp"
    client.start()
