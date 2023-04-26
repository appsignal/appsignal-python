import os
from appsignal.__about__ import __version__

from appsignal.config import (
    Options,
    from_system,
    from_public_environ,
    set_private_environ,
    opentelemetry_resource_attributes,
)


def test_from_system():
    config = from_system()

    assert list(config.keys()) == ["app_path"]


def test_from_public_environ():
    os.environ["APPSIGNAL_APP_ENV"] = "development"
    os.environ["APPSIGNAL_APP_NAME"] = "MyApp"
    os.environ["APPSIGNAL_HOSTNAME"] = "Test hostname"
    os.environ["APPSIGNAL_LOG_LEVEL"] = "trace"
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some-api-key"
    os.environ["APP_REVISION"] = "abc123"

    config = from_public_environ()

    assert config == Options(
        environment="development",
        hostname="Test hostname",
        log_level="trace",
        name="MyApp",
        push_api_key="some-api-key",
        revision="abc123",
    )


def test_from_public_environ_disable_default_instrumentations_list():
    os.environ["APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS"] = ",".join(
        ["opentelemetry.instrumentation.celery", "something.else"]
    )

    config = from_public_environ()

    assert config["disable_default_instrumentations"] == [
        "opentelemetry.instrumentation.celery"
    ]


def test_from_public_environ_disable_default_instrumentations_bool():
    for value, expected in [
        ("True", True),
        ("true", True),
        ("False", False),
        ("false", False),
    ]:
        os.environ["APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS"] = value
        config = from_public_environ()
        assert config["disable_default_instrumentations"] is expected


def test_set_private_environ():
    config = Options(
        environment="development",
        hostname="Test hostname",
        log_level="trace",
        name="MyApp",
        push_api_key="some-api-key",
    )

    set_private_environ(config)

    assert os.environ["_APPSIGNAL_APP_ENV"] == "development"
    assert os.environ["_APPSIGNAL_APP_NAME"] == "MyApp"
    assert os.environ["_APPSIGNAL_HOSTNAME"] == "Test hostname"
    assert os.environ["_APPSIGNAL_LOG_LEVEL"] == "trace"
    assert os.environ["_APPSIGNAL_PUSH_API_KEY"] == "some-api-key"
    assert (
        os.environ["_APPSIGNAL_LANGUAGE_INTEGRATION_VERSION"] == f"python-{__version__}"
    )


def test_opentelemetry_resource_attributes():
    config = Options(
        app_path="/path/to/app",
        revision="abc123",
    )

    attributes = opentelemetry_resource_attributes(config)

    assert attributes == {
        "appsignal.config.app_path": "/path/to/app",
        "appsignal.config.revision": "abc123",
    }
