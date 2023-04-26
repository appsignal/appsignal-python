from __future__ import annotations

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

CONSTANT_PRIVATE_ENVIRON = {"_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP": "true"}

CONSTANT_RESOURCE_ATTRIBUTES = {
    "appsignal.config.language_integration": "python",
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
    app_path: str
    disable_default_instrumentations: Union[list[DefaultInstrumentation], bool]
    environment: str
    hostname: str
    log_level: str
    name: str
    push_api_key: str
    revision: str


def from_system() -> Options:
    return Options(app_path=os.getcwd())


def from_public_environ() -> Options:
    disable_default_instrumentations = parse_disable_default_instrumentations(
        os.environ.get("APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS")
    )

    # We want the type system to ensure that the keys used here are the
    # ones defined in the Options typed dict, but we can't directly use
    # `os.environ.get("APPSIGNAL_WHATEVER")` as their value, as that's an
    # `Optional[str]`, not an `str`. So we use empty strings as the default
    # value, then remove the ones whose values are empty strings.

    config = Options(
        environment=os.environ.get("APPSIGNAL_APP_ENV", ""),
        hostname=os.environ.get("APPSIGNAL_HOSTNAME", ""),
        log_level=os.environ.get("APPSIGNAL_LOG_LEVEL", ""),
        name=os.environ.get("APPSIGNAL_APP_NAME", ""),
        push_api_key=os.environ.get("APPSIGNAL_PUSH_API_KEY", ""),
        revision=os.environ.get("APP_REVISION", ""),
    )

    if disable_default_instrumentations is not None:
        config["disable_default_instrumentations"] = disable_default_instrumentations

    for key, value in list(config.items()):
        if isinstance(value, str) and value == "":
            del cast(dict, config)[key]

    return config


def set_private_environ(config: Options):
    private_environ = {
        "_APPSIGNAL_APP_ENV": config.get("environment"),
        "_APPSIGNAL_APP_NAME": config.get("name"),
        "_APPSIGNAL_HOSTNAME": config.get("hostname"),
        "_APPSIGNAL_LOG_LEVEL": config.get("log_level"),
        "_APPSIGNAL_PUSH_API_KEY": config.get("push_api_key"),
    } | CONSTANT_PRIVATE_ENVIRON

    for var, value in private_environ.items():
        if value is not None:
            os.environ[var] = str(value)


def opentelemetry_resource_attributes(config: Options):
    attributes = {
        k: v
        for k, v in {
            "appsignal.config.app_path": config.get("app_path"),
            "appsignal.config.revision": config.get("revision"),
        }.items()
        if v is not None
    }

    return attributes | CONSTANT_RESOURCE_ATTRIBUTES
