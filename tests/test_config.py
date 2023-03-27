import os

from appsignal.config import (
    Options,
    from_public_environ,
    set_private_environ,
    opentelemetry_resource_attributes,
)


def test_from_public_environ():
    os.environ["APPSIGNAL_APP_NAME"] = "MyApp"
    os.environ["APPSIGNAL_APP_ENV"] = "development"
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some-api-key"
    os.environ["APPSIGNAL_LOG_LEVEL"] = "trace"
    os.environ["APP_REVISION"] = "abc123"

    config = from_public_environ()

    assert config == Options(
        name="MyApp",
        environment="development",
        push_api_key="some-api-key",
        log_level="trace",
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
        name="MyApp",
        environment="development",
        push_api_key="some-api-key",
        log_level="trace",
    )

    set_private_environ(config)

    assert os.environ["_APPSIGNAL_APP_NAME"] == "MyApp"
    assert os.environ["_APPSIGNAL_PUSH_API_KEY"] == "some-api-key"
    assert os.environ["_APPSIGNAL_ENVIRONMENT"] == "development"
    assert os.environ["_APPSIGNAL_LOG_LEVEL"] == "trace"


def test_opentelemetry_resource_attributes():
    config = Options(revision="abc123")

    attributes = opentelemetry_resource_attributes(config)

    assert attributes == {
        "appsignal.config.revision": "abc123",
        "appsignal.config.language_integration": "python",
    }


def test_opentelemetry_resource_attributes_no_revision():
    config = Options()

    attributes = opentelemetry_resource_attributes(config)

    assert attributes == {"appsignal.config.language_integration": "python"}
