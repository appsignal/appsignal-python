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
    app_path: Optional[str]
    disable_default_instrumentations: Optional[
        Union[list[DefaultInstrumentation], bool]
    ]
    enable_host_metrics: Optional[bool]
    environment: Optional[str]
    hostname: Optional[str]
    log_level: Optional[str]
    name: Optional[str]
    push_api_key: Optional[str]
    revision: Optional[str]


def from_system() -> Options:
    return Options(app_path=os.getcwd())


def from_public_environ() -> Options:
    config = Options(
        disable_default_instrumentations=parse_disable_default_instrumentations(
            os.environ.get("APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS")
        ),
        environment=os.environ.get("APPSIGNAL_APP_ENV"),
        hostname=os.environ.get("APPSIGNAL_HOSTNAME"),
        log_level=os.environ.get("APPSIGNAL_LOG_LEVEL"),
        name=os.environ.get("APPSIGNAL_APP_NAME"),
        push_api_key=os.environ.get("APPSIGNAL_PUSH_API_KEY"),
        revision=os.environ.get("APP_REVISION"),
    )

    for key, value in list(config.items()):
        if value is None:
            del cast(dict, config)[key]

    return config


def set_private_environ(config: Options):
    private_environ = {
        "_APPSIGNAL_APP_ENV": config.get("environment"),
        "_APPSIGNAL_APP_NAME": config.get("name"),
        "_APPSIGNAL_APP_PATH": config.get("app_path"),
        "_APPSIGNAL_HOSTNAME": config.get("hostname"),
        "_APPSIGNAL_LOG_LEVEL": config.get("log_level"),
        "_APPSIGNAL_PUSH_API_KEY": config.get("push_api_key"),
        "_APP_REVISION": config.get("revision"),
    } | CONSTANT_PRIVATE_ENVIRON

    for var, value in private_environ.items():
        if value is not None:
            os.environ[var] = str(value)
