import os
from appsignal.__about__ import __version__

from appsignal.config import (
    Options,
    from_system,
    from_public_environ,
    set_private_environ,
)


def test_from_system():
    config = from_system()

    assert list(config.keys()) == ["app_path"]


def test_from_public_environ():
    os.environ["APPSIGNAL_ACTIVE"] = "true"
    os.environ["APPSIGNAL_APP_ENV"] = "development"
    os.environ["APPSIGNAL_APP_NAME"] = "MyApp"
    os.environ["APPSIGNAL_DNS_SERVERS"] = "8.8.8.8,8.8.4.4"
    os.environ["APPSIGNAL_ENABLE_HOST_METRICS"] = "true"
    os.environ["APPSIGNAL_ENABLE_NGINX_METRICS"] = "false"
    os.environ["APPSIGNAL_ENABLE_STATSD"] = "false"
    os.environ["APPSIGNAL_FILES_WORLD_ACCESSIBLE"] = "true"
    os.environ["APPSIGNAL_FILTER_PARAMETERS"] = "password,secret"
    os.environ["APPSIGNAL_FILTER_SESSION_DATA"] = "key1,key2"
    os.environ["APPSIGNAL_HOSTNAME"] = "Test hostname"
    os.environ["APPSIGNAL_IGNORE_ACTIONS"] = "action1,action2"
    os.environ["APPSIGNAL_IGNORE_ERRORS"] = "error1,error2"
    os.environ["APPSIGNAL_IGNORE_NAMESPACES"] = "namespace1,namespace2"
    os.environ["APPSIGNAL_LOG_LEVEL"] = "trace"
    os.environ["APPSIGNAL_PUSH_API_KEY"] = "some-api-key"
    os.environ["APPSIGNAL_RUNNING_IN_CONTAINER"] = "true"
    os.environ["APPSIGNAL_SEND_ENVIRONMENT_METADATA"] = "true"
    os.environ["APPSIGNAL_SEND_PARAMS"] = "true"
    os.environ["APPSIGNAL_SEND_SESSION_DATA"] = "true"
    os.environ["APP_REVISION"] = "abc123"

    config = from_public_environ()

    assert config == Options(
        active=True,
        dns_servers=["8.8.8.8", "8.8.4.4"],
        enable_host_metrics=True,
        enable_nginx_metrics=False,
        enable_statsd=False,
        environment="development",
        files_world_accessible=True,
        filter_parameters=["password", "secret"],
        filter_session_data=["key1", "key2"],
        hostname="Test hostname",
        ignore_actions=["action1", "action2"],
        ignore_errors=["error1", "error2"],
        ignore_namespaces=["namespace1", "namespace2"],
        log_level="trace",
        name="MyApp",
        push_api_key="some-api-key",
        revision="abc123",
        running_in_container=True,
        send_environment_metadata=True,
        send_params=True,
        send_session_data=True,
    )


def test_from_public_environ_bool_is_unset():
    config = from_public_environ()

    assert config.get("active") is None


def test_from_public_environ_bool_is_empty_string():
    os.environ["APPSIGNAL_ACTIVE"] = ""

    config = from_public_environ()

    assert config.get("active") is None


def test_from_public_environ_bool_is_invalid():
    os.environ["APPSIGNAL_ACTIVE"] = "invalid"

    config = from_public_environ()

    assert config.get("active") is None


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
        active=True,
        app_path="/path/to/app",
        dns_servers=["8.8.8.8", "8.8.4.4"],
        enable_host_metrics=True,
        enable_nginx_metrics=False,
        enable_statsd=False,
        environment="development",
        files_world_accessible=True,
        filter_parameters=["password", "secret"],
        filter_session_data=["key1", "key2"],
        hostname="Test hostname",
        ignore_actions=["action1", "action2"],
        ignore_errors=["error1", "error2"],
        ignore_namespaces=["namespace1", "namespace2"],
        log_level="trace",
        name="MyApp",
        push_api_key="some-api-key",
        revision="abc123",
        running_in_container=True,
        send_environment_metadata=True,
        send_params=True,
        send_session_data=True,
    )

    set_private_environ(config)

    assert os.environ["_APPSIGNAL_ACTIVE"] == "true"
    assert os.environ["_APPSIGNAL_APP_ENV"] == "development"
    assert os.environ["_APPSIGNAL_APP_NAME"] == "MyApp"
    assert os.environ["_APPSIGNAL_APP_PATH"] == "/path/to/app"
    assert os.environ["_APPSIGNAL_DNS_SERVERS"] == "8.8.8.8,8.8.4.4"
    assert os.environ["_APPSIGNAL_ENABLE_HOST_METRICS"] == "true"
    assert os.environ["_APPSIGNAL_ENABLE_NGINX_METRICS"] == "false"
    assert os.environ["_APPSIGNAL_ENABLE_STATSD"] == "false"
    assert os.environ["_APPSIGNAL_FILES_WORLD_ACCESSIBLE"] == "true"
    assert os.environ["_APPSIGNAL_FILTER_PARAMETERS"] == "password,secret"
    assert os.environ["_APPSIGNAL_FILTER_SESSION_DATA"] == "key1,key2"
    assert os.environ["_APPSIGNAL_HOSTNAME"] == "Test hostname"
    assert os.environ["_APPSIGNAL_IGNORE_ACTIONS"] == "action1,action2"
    assert os.environ["_APPSIGNAL_IGNORE_ERRORS"] == "error1,error2"
    assert os.environ["_APPSIGNAL_IGNORE_NAMESPACES"] == "namespace1,namespace2"
    assert os.environ["_APPSIGNAL_LOG_LEVEL"] == "trace"
    assert os.environ["_APPSIGNAL_PUSH_API_KEY"] == "some-api-key"
    assert (
        os.environ["_APPSIGNAL_LANGUAGE_INTEGRATION_VERSION"] == f"python-{__version__}"
    )
    assert os.environ["_APPSIGNAL_RUNNING_IN_CONTAINER"] == "true"
    assert os.environ["_APPSIGNAL_SEND_ENVIRONMENT_METADATA"] == "true"
    assert os.environ["_APPSIGNAL_SEND_PARAMS"] == "true"
    assert os.environ["_APPSIGNAL_SEND_SESSION_DATA"] == "true"
    assert os.environ["_APP_REVISION"] == "abc123"


def test_set_private_environ_bool_is_none():
    config = Options(
        active=None,
    )

    set_private_environ(config)

    assert os.environ.get("_APPSIGNAL_ACTIVE") is None


def test_set_private_environ_list_is_none():
    config = Options(
        dns_servers=None,
    )

    set_private_environ(config)

    assert os.environ.get("_APPSIGNAL_DNS_SERVERS") is None
