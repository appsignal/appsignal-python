from __future__ import annotations
from .__about__ import __version__

import os
from typing import cast, get_args, TypedDict, Union, Optional, Literal

DefaultInstrumentation = Literal[
    "opentelemetry.instrumentation.celery",
    "opentelemetry.instrumentation.django",
    "opentelemetry.instrumentation.jinja2",
    "opentelemetry.instrumentation.psycopg2",
    "opentelemetry.instrumentation.redis",
    "opentelemetry.instrumentation.requests",
]

DEFAULT_INSTRUMENTATIONS = cast(
    list[DefaultInstrumentation], list(get_args(DefaultInstrumentation))
)

CONSTANT_PRIVATE_ENVIRON = {
    "_APPSIGNAL_LANGUAGE_INTEGRATION_VERSION": f"python-{__version__}",
    "_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP": "true",
}


def parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None

    val = value.lower()
    if val == "true":
        return True
    if val == "false":
        return False

    return None


def parse_disable_default_instrumentations(
    value: Optional[str],
) -> Optional[Union[list[DefaultInstrumentation], bool]]:
    if value is None:
        return None

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    return cast(
        list[DefaultInstrumentation],
        [x for x in value.split(",") if x in DEFAULT_INSTRUMENTATIONS],
    )


class Options(TypedDict, total=False):
    active: Optional[bool]
    app_path: Optional[str]
    disable_default_instrumentations: Optional[
        Union[list[DefaultInstrumentation], bool]
    ]
    enable_host_metrics: Optional[bool]
    enable_nginx_metrics: Optional[bool]
    enable_statsd: Optional[bool]
    environment: Optional[str]
    files_world_accessible: Optional[bool]
    hostname: Optional[str]
    log_level: Optional[str]
    name: Optional[str]
    push_api_key: Optional[str]
    revision: Optional[str]
    running_in_container: Optional[bool]
    send_environment_metadata: Optional[bool]
    send_params: Optional[bool]
    send_session_data: Optional[bool]


DEFAULT_CONFIG = Options(
    enable_host_metrics=True,
    enable_nginx_metrics=False,
    enable_statsd=False,
    files_world_accessible=True,
    send_environment_metadata=True,
    send_params=True,
    send_session_data=True,
)


def from_system() -> Options:
    return Options(app_path=os.getcwd())


def from_public_environ() -> Options:
    config = Options(
        active=parse_bool(os.environ.get("APPSIGNAL_ACTIVE")),
        disable_default_instrumentations=parse_disable_default_instrumentations(
            os.environ.get("APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS")
        ),
        enable_host_metrics=parse_bool(os.environ.get("APPSIGNAL_ENABLE_HOST_METRICS")),
        enable_nginx_metrics=parse_bool(
            os.environ.get("APPSIGNAL_ENABLE_NGINX_METRICS")
        ),
        enable_statsd=parse_bool(os.environ.get("APPSIGNAL_ENABLE_STATSD")),
        environment=os.environ.get("APPSIGNAL_APP_ENV"),
        files_world_accessible=parse_bool(
            os.environ.get("APPSIGNAL_FILES_WORLD_ACCESSIBLE")
        ),
        hostname=os.environ.get("APPSIGNAL_HOSTNAME"),
        log_level=os.environ.get("APPSIGNAL_LOG_LEVEL"),
        name=os.environ.get("APPSIGNAL_APP_NAME"),
        push_api_key=os.environ.get("APPSIGNAL_PUSH_API_KEY"),
        revision=os.environ.get("APP_REVISION"),
        running_in_container=parse_bool(
            os.environ.get("APPSIGNAL_RUNNING_IN_CONTAINER")
        ),
        send_environment_metadata=parse_bool(
            os.environ.get("APPSIGNAL_SEND_ENVIRONMENT_METADATA")
        ),
        send_params=parse_bool(os.environ.get("APPSIGNAL_SEND_PARAMS")),
        send_session_data=parse_bool(os.environ.get("APPSIGNAL_SEND_SESSION_DATA")),
    )

    for key, value in list(config.items()):
        if value is None:
            del cast(dict, config)[key]

    return config


def bool_to_env_str(value: Optional[bool]):
    if value is None:
        return None

    return str(value).lower()


def set_private_environ(config: Options):
    private_environ = {
        "_APPSIGNAL_ACTIVE": bool_to_env_str(config.get("active")),
        "_APPSIGNAL_APP_ENV": config.get("environment"),
        "_APPSIGNAL_APP_NAME": config.get("name"),
        "_APPSIGNAL_APP_PATH": config.get("app_path"),
        "_APPSIGNAL_ENABLE_HOST_METRICS": bool_to_env_str(
            config.get("enable_host_metrics")
        ),
        "_APPSIGNAL_ENABLE_NGINX_METRICS": bool_to_env_str(
            config.get("enable_nginx_metrics")
        ),
        "_APPSIGNAL_ENABLE_STATSD": bool_to_env_str(config.get("enable_statsd")),
        "_APPSIGNAL_FILES_WORLD_ACCESSIBLE": bool_to_env_str(
            config.get("files_world_accessible")
        ),
        "_APPSIGNAL_HOSTNAME": config.get("hostname"),
        "_APPSIGNAL_LOG_LEVEL": config.get("log_level"),
        "_APPSIGNAL_PUSH_API_KEY": config.get("push_api_key"),
        "_APPSIGNAL_RUNNING_IN_CONTAINER": bool_to_env_str(
            config.get("running_in_container")
        ),
        "_APPSIGNAL_SEND_ENVIRONMENT_METADATA": bool_to_env_str(
            config.get("send_environment_metadata")
        ),
        "_APPSIGNAL_SEND_PARAMS": bool_to_env_str(config.get("send_params")),
        "_APPSIGNAL_SEND_SESSION_DATA": bool_to_env_str(
            config.get("send_session_data")
        ),
        "_APP_REVISION": config.get("revision"),
    } | CONSTANT_PRIVATE_ENVIRON

    for var, value in private_environ.items():
        if value is not None:
            os.environ[var] = str(value)
