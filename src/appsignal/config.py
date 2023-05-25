from __future__ import annotations
from .__about__ import __version__
from typing import List

import os
import platform
import tempfile
from typing import TYPE_CHECKING, cast, get_args, TypedDict, Union, Optional, Literal

if TYPE_CHECKING:
    pass


class Options(TypedDict, total=False):
    active: Optional[bool]
    app_path: Optional[str]
    ca_file_path: Optional[str]
    disable_default_instrumentations: Optional[
        Union[list[Config.DefaultInstrumentation], bool]
    ]
    dns_servers: Optional[list[str]]
    enable_host_metrics: Optional[bool]
    enable_nginx_metrics: Optional[bool]
    enable_statsd: Optional[bool]
    endpoint: Optional[str]
    environment: Optional[str]
    files_world_accessible: Optional[bool]
    filter_parameters: Optional[list[str]]
    filter_session_data: Optional[list[str]]
    hostname: Optional[str]
    http_proxy: Optional[str]
    ignore_actions: Optional[list[str]]
    ignore_errors: Optional[list[str]]
    ignore_namespaces: Optional[list[str]]
    log: Optional[str]
    log_level: Optional[str]
    log_path: Optional[str]
    name: Optional[str]
    push_api_key: Optional[str]
    revision: Optional[str]
    request_headers: Optional[list[str]]
    running_in_container: Optional[bool]
    send_environment_metadata: Optional[bool]
    send_params: Optional[bool]
    send_session_data: Optional[bool]
    working_directory_path: Optional[str]


class Sources(TypedDict):
    default: Options
    system: Options
    initial: Options
    environment: Options


class Config:
    sources: Sources

    CA_FILE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "resources", "cacert.pem"
    )
    DEFAULT_CONFIG = Options(
        ca_file_path=CA_FILE_PATH,
        enable_host_metrics=True,
        enable_nginx_metrics=False,
        enable_statsd=False,
        environment="development",
        endpoint="https://push.appsignal.com",
        files_world_accessible=True,
        log="file",
        log_level="info",
        send_environment_metadata=True,
        send_params=True,
        send_session_data=True,
        request_headers=[
            "accept",
            "accept-charset",
            "accept-encoding",
            "accept-language",
            "cache-control",
            "connection",
            "content-length",
            "range",
        ],
    )

    DefaultInstrumentation = Literal[
        "opentelemetry.instrumentation.celery",
        "opentelemetry.instrumentation.django",
        "opentelemetry.instrumentation.flask",
        "opentelemetry.instrumentation.jinja2",
        "opentelemetry.instrumentation.psycopg2",
        "opentelemetry.instrumentation.redis",
        "opentelemetry.instrumentation.requests",
    ]
    DEFAULT_INSTRUMENTATIONS = cast(
        List[DefaultInstrumentation], list(get_args(DefaultInstrumentation))
    )

    def __init__(self, options: Optional[Options] = None):
        self.sources = Sources(
            default=self.DEFAULT_CONFIG,
            system=Config.load_from_system(),
            initial=options or Options(),
            environment=Config.load_from_environment(),
        )
        final_options = Options()
        final_options.update(self.sources["default"])
        final_options.update(self.sources["system"])
        final_options.update(self.sources["initial"])
        final_options.update(self.sources["environment"])
        self.options = final_options

    def option(self, option: str):
        return self.options.get(option)

    @classmethod
    def load_from_system(_cls) -> Options:
        return Options(app_path=os.getcwd())

    @classmethod
    def load_from_environment(_cls) -> Options:
        options = Options(
            active=parse_bool(os.environ.get("APPSIGNAL_ACTIVE")),
            ca_file_path=os.environ.get("APPSIGNAL_CA_FILE_PATH"),
            disable_default_instrumentations=parse_disable_default_instrumentations(
                os.environ.get("APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS")
            ),
            dns_servers=parse_list(os.environ.get("APPSIGNAL_DNS_SERVERS")),
            enable_host_metrics=parse_bool(
                os.environ.get("APPSIGNAL_ENABLE_HOST_METRICS")
            ),
            enable_nginx_metrics=parse_bool(
                os.environ.get("APPSIGNAL_ENABLE_NGINX_METRICS")
            ),
            enable_statsd=parse_bool(os.environ.get("APPSIGNAL_ENABLE_STATSD")),
            endpoint=os.environ.get("APPSIGNAL_PUSH_API_ENDPOINT"),
            environment=os.environ.get("APPSIGNAL_APP_ENV"),
            files_world_accessible=parse_bool(
                os.environ.get("APPSIGNAL_FILES_WORLD_ACCESSIBLE")
            ),
            filter_parameters=parse_list(os.environ.get("APPSIGNAL_FILTER_PARAMETERS")),
            filter_session_data=parse_list(
                os.environ.get("APPSIGNAL_FILTER_SESSION_DATA")
            ),
            hostname=os.environ.get("APPSIGNAL_HOSTNAME"),
            http_proxy=os.environ.get("APPSIGNAL_HTTP_PROXY"),
            ignore_actions=parse_list(os.environ.get("APPSIGNAL_IGNORE_ACTIONS")),
            ignore_errors=parse_list(os.environ.get("APPSIGNAL_IGNORE_ERRORS")),
            ignore_namespaces=parse_list(os.environ.get("APPSIGNAL_IGNORE_NAMESPACES")),
            log=os.environ.get("APPSIGNAL_LOG"),
            log_level=os.environ.get("APPSIGNAL_LOG_LEVEL"),
            log_path=os.environ.get("APPSIGNAL_LOG_PATH"),
            name=os.environ.get("APPSIGNAL_APP_NAME"),
            push_api_key=os.environ.get("APPSIGNAL_PUSH_API_KEY"),
            revision=os.environ.get("APP_REVISION"),
            request_headers=parse_list(os.environ.get("APPSIGNAL_REQUEST_HEADERS")),
            running_in_container=parse_bool(
                os.environ.get("APPSIGNAL_RUNNING_IN_CONTAINER")
            ),
            send_environment_metadata=parse_bool(
                os.environ.get("APPSIGNAL_SEND_ENVIRONMENT_METADATA")
            ),
            send_params=parse_bool(os.environ.get("APPSIGNAL_SEND_PARAMS")),
            send_session_data=parse_bool(os.environ.get("APPSIGNAL_SEND_SESSION_DATA")),
            working_directory_path=os.environ.get("APPSIGNAL_WORKING_DIRECTORY_PATH"),
        )

        for key, value in list(options.items()):
            if value is None:
                del cast(dict, options)[key]

        return options

    CONSTANT_PRIVATE_ENVIRON = {
        "_APPSIGNAL_LANGUAGE_INTEGRATION_VERSION": f"python-{__version__}",
        "_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP": "true",
    }

    def set_private_environ(self):
        options = self.options
        private_environ = {
            "_APPSIGNAL_ACTIVE": bool_to_env_str(options.get("active")),
            "_APPSIGNAL_APP_ENV": options.get("environment"),
            "_APPSIGNAL_APP_NAME": options.get("name"),
            "_APPSIGNAL_APP_PATH": options.get("app_path"),
            "_APPSIGNAL_CA_FILE_PATH": options.get("ca_file_path"),
            "_APPSIGNAL_DNS_SERVERS": list_to_env_str(options.get("dns_servers")),
            "_APPSIGNAL_ENABLE_HOST_METRICS": bool_to_env_str(
                options.get("enable_host_metrics")
            ),
            "_APPSIGNAL_ENABLE_NGINX_METRICS": bool_to_env_str(
                options.get("enable_nginx_metrics")
            ),
            "_APPSIGNAL_ENABLE_STATSD": bool_to_env_str(options.get("enable_statsd")),
            "_APPSIGNAL_FILES_WORLD_ACCESSIBLE": bool_to_env_str(
                options.get("files_world_accessible")
            ),
            "_APPSIGNAL_FILTER_PARAMETERS": list_to_env_str(
                options.get("filter_parameters")
            ),
            "_APPSIGNAL_FILTER_SESSION_DATA": list_to_env_str(
                options.get("filter_session_data")
            ),
            "_APPSIGNAL_HOSTNAME": options.get("hostname"),
            "_APPSIGNAL_HTTP_PROXY": options.get("http_proxy"),
            "_APPSIGNAL_IGNORE_ACTIONS": list_to_env_str(options.get("ignore_actions")),
            "_APPSIGNAL_IGNORE_ERRORS": list_to_env_str(options.get("ignore_errors")),
            "_APPSIGNAL_IGNORE_NAMESPACES": list_to_env_str(
                options.get("ignore_namespaces")
            ),
            "_APPSIGNAL_LOG": options.get("log"),
            "_APPSIGNAL_LOG_LEVEL": options.get("log_level"),
            "_APPSIGNAL_LOG_FILE_PATH": self.log_file_path(),
            "_APPSIGNAL_PUSH_API_KEY": options.get("push_api_key"),
            "_APPSIGNAL_PUSH_API_ENDPOINT": options.get("endpoint"),
            "_APPSIGNAL_RUNNING_IN_CONTAINER": bool_to_env_str(
                options.get("running_in_container")
            ),
            "_APPSIGNAL_SEND_ENVIRONMENT_METADATA": bool_to_env_str(
                options.get("send_environment_metadata")
            ),
            "_APPSIGNAL_SEND_PARAMS": bool_to_env_str(options.get("send_params")),
            "_APPSIGNAL_SEND_SESSION_DATA": bool_to_env_str(
                options.get("send_session_data")
            ),
            "_APPSIGNAL_WORKING_DIRECTORY_PATH": options.get("working_directory_path"),
            "_APP_REVISION": options.get("revision"),
        }
        private_environ.update(self.CONSTANT_PRIVATE_ENVIRON)

        for var, value in private_environ.items():
            if value is not None:
                os.environ[var] = str(value)

    def log_file_path(self) -> Optional[str]:
        path = self.options.get("log_path")

        if path:
            _, ext = os.path.splitext(path)
            if ext:
                path = os.path.dirname(path)

            if not os.access(path, os.W_OK):
                print(
                    f"appsignal: Unable to write to configured '{path}'. Please "
                    "check the permissions of the 'log_path' directory."
                )
                path = None

        if not path:
            path = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()

        if not os.access(path, os.W_OK):
            print(
                f"appsignal: Unable to write to '{path}'. Please check the "
                "permissions of the 'log_path' directory."
            )
            return None
        return os.path.join(path, "appsignal.log")


def parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None

    val = value.lower()
    if val == "true":
        return True
    if val == "false":
        return False

    return None


def parse_list(value: Optional[str]) -> Optional[list[str]]:
    if value is None:
        return None

    return value.split(",")


def parse_disable_default_instrumentations(
    value: Optional[str],
) -> Optional[Union[list[Config.DefaultInstrumentation], bool]]:
    if value is None:
        return None

    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    return cast(
        List[Config.DefaultInstrumentation],
        [x for x in value.split(",") if x in Config.DEFAULT_INSTRUMENTATIONS],
    )


def bool_to_env_str(value: Optional[bool]):
    if value is None:
        return None

    return str(value).lower()


def list_to_env_str(value: Optional[list[str]]):
    if value is None:
        return None

    return ",".join(value)
