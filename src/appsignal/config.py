from __future__ import annotations

import os
import platform
import socket
import tempfile
from typing import Any, ClassVar, List, Literal, TypedDict, cast, get_args

from . import internal_logger as logger
from .__about__ import __version__


class Options(TypedDict, total=False):
    active: bool | None
    app_path: str | None
    bind_address: str | None
    ca_file_path: str | None
    collector_endpoint: str | None
    cpu_count: float | None
    diagnose_endpoint: str | None
    disable_default_instrumentations: None | (
        list[Config.DefaultInstrumentation] | bool
    )
    dns_servers: list[str] | None
    enable_host_metrics: bool | None
    enable_minutely_probes: bool | None
    enable_nginx_metrics: bool | None
    enable_statsd: bool | None
    endpoint: str | None
    environment: str | None
    files_world_accessible: bool | None
    filter_attributes: list[str] | None
    filter_function_parameters: list[str] | None
    filter_parameters: list[str] | None
    filter_request_payload: list[str] | None
    filter_request_query_parameters: list[str] | None
    filter_session_data: list[str] | None
    hostname: str | None
    host_role: str | None
    http_proxy: str | None
    ignore_actions: list[str] | None
    ignore_errors: list[str] | None
    ignore_namespaces: list[str] | None
    log: str | None
    log_level: str | None
    log_path: str | None
    logging_endpoint: str | None
    nginx_port: str | int | None
    opentelemetry_port: str | int | None
    name: str | None
    push_api_key: str | None
    revision: str | None
    request_headers: list[str] | None
    response_headers: list[str] | None
    running_in_container: bool | None
    send_environment_metadata: bool | None
    send_function_parameters: bool | None
    send_params: bool | None
    send_request_payload: bool | None
    send_request_query_parameters: bool | None
    send_session_data: bool | None
    service_name: str | None
    statsd_port: str | int | None
    working_directory_path: str | None


class Sources(TypedDict):
    default: Options
    system: Options
    initial: Options
    environment: Options


class Config:
    valid: bool
    sources: Sources

    CA_FILE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "resources", "cacert.pem"
    )
    DEFAULT_ENVIRONMENT = "development"
    DEFAULT_CONFIG = Options(
        ca_file_path=CA_FILE_PATH,
        diagnose_endpoint="https://appsignal.com/diag",
        enable_host_metrics=True,
        enable_minutely_probes=True,
        enable_nginx_metrics=False,
        enable_statsd=False,
        environment=DEFAULT_ENVIRONMENT,
        endpoint="https://push.appsignal.com",
        files_world_accessible=True,
        log="file",
        log_level="info",
        logging_endpoint="https://appsignal-endpoint.net",
        opentelemetry_port=8099,
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
        "aiopg",
        "asyncpg",
        "celery",
        "django",
        "flask",
        "jinja2",
        "mysql",
        "mysqlclient",
        "pika",
        "psycopg",
        "psycopg2",
        "pymysql",
        "redis",
        "requests",
        "sqlite3",
        "sqlalchemy",
        "logging",
    ]
    DEFAULT_INSTRUMENTATIONS = cast(
        List[DefaultInstrumentation], list(get_args(DefaultInstrumentation))
    )

    def __init__(self, options: Options | None = None) -> None:
        self.valid = False
        self.sources = Sources(
            default=self.DEFAULT_CONFIG,
            system=Config.load_from_system(),
            initial=options or Options(),
            environment=Config.load_from_environment(),
        )
        final_options = Options()
        final_options.update(self.sources["default"])
        final_options.update(self.sources["system"])
        final_options.update(self.sources["environment"])
        final_options.update(self.sources["initial"])
        self.options = final_options
        self._validate()

    def is_active(self) -> bool:
        return self.valid and self.option("active")

    def option(self, option: str) -> Any:
        return self.options.get(option)

    # Whether it should instrument logging.
    def should_instrument_logging(self) -> bool:
        # The agent does not support logging, so this is equivalent
        # to whether it should use a collector.
        return self.should_use_collector()

    # Whether it should use a collector to send data to AppSignal.
    def should_use_collector(self) -> bool:
        # This is currently equivalent to whether it should use an
        # external collector.
        return self.should_use_external_collector()

    # Whether it should use a collector to send data to AppSignal
    # which is booted externally to this integration.
    def should_use_external_collector(self) -> bool:
        return self.option("collector_endpoint") is not None

    @staticmethod
    def load_from_system() -> Options:
        return Options(
            app_path=os.getcwd(),
            hostname=os.environ.get("HOSTNAME") or socket.gethostname(),
        )

    @staticmethod
    def load_from_environment() -> Options:
        options = Options(
            active=parse_bool(os.environ.get("APPSIGNAL_ACTIVE")),
            bind_address=os.environ.get("APPSIGNAL_BIND_ADDRESS"),
            ca_file_path=os.environ.get("APPSIGNAL_CA_FILE_PATH"),
            collector_endpoint=os.environ.get("APPSIGNAL_COLLECTOR_ENDPOINT"),
            cpu_count=parse_float(os.environ.get("APPSIGNAL_CPU_COUNT")),
            diagnose_endpoint=os.environ.get("APPSIGNAL_DIAGNOSE_ENDPOINT"),
            disable_default_instrumentations=parse_disable_default_instrumentations(
                os.environ.get("APPSIGNAL_DISABLE_DEFAULT_INSTRUMENTATIONS")
            ),
            dns_servers=parse_list(os.environ.get("APPSIGNAL_DNS_SERVERS")),
            enable_host_metrics=parse_bool(
                os.environ.get("APPSIGNAL_ENABLE_HOST_METRICS")
            ),
            enable_minutely_probes=parse_bool(
                os.environ.get("APPSIGNAL_ENABLE_MINUTELY_PROBES")
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
            filter_attributes=parse_list(os.environ.get("APPSIGNAL_FILTER_ATTRIBUTES")),
            filter_function_parameters=parse_list(
                os.environ.get("APPSIGNAL_FILTER_FUNCTION_PARAMETERS")
            ),
            filter_parameters=parse_list(os.environ.get("APPSIGNAL_FILTER_PARAMETERS")),
            filter_request_payload=parse_list(
                os.environ.get("APPSIGNAL_FILTER_REQUEST_PAYLOAD")
            ),
            filter_request_query_parameters=parse_list(
                os.environ.get("APPSIGNAL_FILTER_REQUEST_QUERY_PARAMETERS")
            ),
            filter_session_data=parse_list(
                os.environ.get("APPSIGNAL_FILTER_SESSION_DATA")
            ),
            hostname=os.environ.get("APPSIGNAL_HOSTNAME"),
            host_role=os.environ.get("APPSIGNAL_HOST_ROLE"),
            http_proxy=os.environ.get("APPSIGNAL_HTTP_PROXY"),
            ignore_actions=parse_list(os.environ.get("APPSIGNAL_IGNORE_ACTIONS")),
            ignore_errors=parse_list(os.environ.get("APPSIGNAL_IGNORE_ERRORS")),
            ignore_namespaces=parse_list(os.environ.get("APPSIGNAL_IGNORE_NAMESPACES")),
            log=os.environ.get("APPSIGNAL_LOG"),
            log_level=os.environ.get("APPSIGNAL_LOG_LEVEL"),
            log_path=os.environ.get("APPSIGNAL_LOG_PATH"),
            logging_endpoint=os.environ.get("APPSIGNAL_LOGGING_ENDPOINT"),
            nginx_port=os.environ.get("APPSIGNAL_NGINX_PORT"),
            opentelemetry_port=os.environ.get("APPSIGNAL_OPENTELEMETRY_PORT"),
            name=os.environ.get("APPSIGNAL_APP_NAME"),
            push_api_key=os.environ.get("APPSIGNAL_PUSH_API_KEY"),
            revision=os.environ.get("APP_REVISION"),
            request_headers=parse_list(os.environ.get("APPSIGNAL_REQUEST_HEADERS")),
            response_headers=parse_list(os.environ.get("APPSIGNAL_RESPONSE_HEADERS")),
            running_in_container=parse_bool(
                os.environ.get("APPSIGNAL_RUNNING_IN_CONTAINER")
            ),
            send_environment_metadata=parse_bool(
                os.environ.get("APPSIGNAL_SEND_ENVIRONMENT_METADATA")
            ),
            send_function_parameters=parse_bool(
                os.environ.get("APPSIGNAL_SEND_FUNCTION_PARAMETERS")
            ),
            send_params=parse_bool(os.environ.get("APPSIGNAL_SEND_PARAMS")),
            send_request_payload=parse_bool(
                os.environ.get("APPSIGNAL_SEND_REQUEST_PAYLOAD")
            ),
            send_request_query_parameters=parse_bool(
                os.environ.get("APPSIGNAL_SEND_REQUEST_QUERY_PARAMETERS")
            ),
            send_session_data=parse_bool(os.environ.get("APPSIGNAL_SEND_SESSION_DATA")),
            service_name=os.environ.get("APPSIGNAL_SERVICE_NAME"),
            statsd_port=os.environ.get("APPSIGNAL_STATSD_PORT"),
            working_directory_path=os.environ.get("APPSIGNAL_WORKING_DIRECTORY_PATH"),
        )

        for key, value in list(options.items()):
            if value is None:
                del cast(dict, options)[key]

        return options

    CONSTANT_PRIVATE_ENVIRON: ClassVar[dict[str, str]] = {
        "_APPSIGNAL_LANGUAGE_INTEGRATION_VERSION": f"python-{__version__}",
        "_APPSIGNAL_ENABLE_OPENTELEMETRY_HTTP": "true",
    }

    def set_private_environ(self) -> None:
        options = self.options
        private_environ = {
            "_APPSIGNAL_ACTIVE": bool_to_env_str(options.get("active")),
            "_APPSIGNAL_APP_ENV": options.get("environment"),
            "_APPSIGNAL_APP_NAME": options.get("name"),
            "_APPSIGNAL_APP_PATH": options.get("app_path"),
            "_APPSIGNAL_BIND_ADDRESS": options.get("bind_address"),
            "_APPSIGNAL_CA_FILE_PATH": options.get("ca_file_path"),
            "_APPSIGNAL_CPU_COUNT": float_to_env_str(options.get("cpu_count")),
            "_APPSIGNAL_DNS_SERVERS": list_to_env_str(options.get("dns_servers")),
            "_APPSIGNAL_DIAGNOSE_ENDPOINT": options.get("diagnose_endpoint"),
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
            "_APPSIGNAL_HOST_ROLE": options.get("host_role"),
            "_APPSIGNAL_HTTP_PROXY": options.get("http_proxy"),
            "_APPSIGNAL_IGNORE_ACTIONS": list_to_env_str(options.get("ignore_actions")),
            "_APPSIGNAL_IGNORE_ERRORS": list_to_env_str(options.get("ignore_errors")),
            "_APPSIGNAL_IGNORE_NAMESPACES": list_to_env_str(
                options.get("ignore_namespaces")
            ),
            "_APPSIGNAL_LOG": options.get("log"),
            "_APPSIGNAL_LOG_LEVEL": options.get("log_level"),
            "_APPSIGNAL_LOG_FILE_PATH": self.log_file_path(),
            "_APPSIGNAL_LOGGING_ENDPOINT": options.get("logging_endpoint"),
            "_APPSIGNAL_NGINX_PORT": options.get("nginx_port"),
            "_APPSIGNAL_OPENTELEMETRY_PORT": options.get("opentelemetry_port"),
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
            "_APPSIGNAL_STATSD_PORT": options.get("statsd_port"),
            "_APPSIGNAL_WORKING_DIRECTORY_PATH": options.get("working_directory_path"),
            "_APP_REVISION": options.get("revision"),
        }
        private_environ.update(self.CONSTANT_PRIVATE_ENVIRON)

        for var, value in private_environ.items():
            if value is not None:
                os.environ[var] = str(value)

    def log_file_path(self) -> str | None:
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

    def _validate(self) -> None:
        if self.option("active") is not True:
            # Only validate if config is active to avoid unnecessary output
            return

        push_api_key = self.option("push_api_key") or ""
        if len(push_api_key.strip()) > 0:
            self.valid = True

    def warn(self) -> None:
        if self.should_use_collector():
            self._warn_agent_exclusive_options()
        else:
            self._warn_collector_exclusive_options()

    # Emit a warning if agent-exclusive configuration options are used.
    def _warn_agent_exclusive_options(self) -> None:
        agent_exclusive_options = [
            "bind_address",
            "cpu_count",
            "dns_servers",
            "enable_host_metrics",
            "enable_nginx_metrics",
            "enable_statsd",
            "files_world_accessible",
            "filter_parameters",
            "host_role",
            "nginx_port",
            "opentelemetry_port",
            "running_in_container",
            "send_environment_metadata",
            "send_params",
            "working_directory_path",
            "statsd_port",
        ]

        option_specific_warnings = {
            "filter_parameters": (
                "Use the 'filter_attributes', 'filter_function_parameters',"
                " 'filter_request_payload' and 'filter_request_query_parameters'"
                " configuration options instead."
            ),
            "send_params": (
                "Use the 'send_function_parameters', 'send_request_payload'"
                " and 'send_request_query_parameters' configuration options instead."
            ),
            "opentelemetry_port": (
                "Set the collector's OpenTelemetry port as part of the"
                " 'collector_endpoint' configuration option."
            ),
        }

        non_default_options = self._filter_non_default_options(agent_exclusive_options)

        for option in non_default_options:
            logger.warning(
                f"The collector is in use. The '{option}' configuration option"
                " is only used by the agent and will be ignored."
            )
            if option in option_specific_warnings:
                logger.warning(option_specific_warnings[option])

        if non_default_options:
            logger.info(
                "To use the agent, unset the 'collector_endpoint' configuration option."
            )

    # Emit a warning if collector-exclusive configuration options are used.
    def _warn_collector_exclusive_options(self) -> None:
        collector_exclusive_options = [
            "filter_attributes",
            "filter_function_parameters",
            "filter_request_payload",
            "filter_request_query_parameters",
            "response_headers",
            "send_function_parameters",
            "send_request_payload",
            "send_request_query_parameters",
        ]

        filter_warning = "Use the 'filter_parameters' option instead."
        send_warning = "Use the 'send_params' option instead."

        option_specific_warnings = {
            "filter_attributes": filter_warning,
            "filter_function_parameters": filter_warning,
            "filter_request_payload": filter_warning,
            "filter_request_query_parameters": filter_warning,
            "send_function_parameters": send_warning,
            "send_request_payload": send_warning,
            "send_request_query_parameters": send_warning,
        }

        non_default_options = self._filter_non_default_options(
            collector_exclusive_options
        )

        for option in non_default_options:
            logger.warning(
                f"The agent is in use. The '{option}' configuration option"
                " is only used by the collector and will be ignored."
            )
            if option in option_specific_warnings:
                logger.warning(option_specific_warnings[option])

        if non_default_options:
            logger.info(
                "To use the collector, set the 'collector_endpoint' configuration option."
            )

    # Filter a list of options, returning a list of those options for which
    # the value differs from that of the default configuration.
    def _filter_non_default_options(self, options: list[str]) -> list[str]:
        return [
            option
            for option in options
            if self.option(option) != self.sources["default"].get(option)
        ]


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None

    val = value.lower()
    if val == "true":
        return True
    if val == "false":
        return False

    return None


def parse_list(value: str | None) -> list[str] | None:
    if value is None:
        return None

    return value.split(",")


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def parse_disable_default_instrumentations(
    value: str | None,
) -> list[Config.DefaultInstrumentation] | bool | None:
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


def bool_to_env_str(value: bool | None) -> str | None:
    if value is None:
        return None

    return str(value).lower()


def list_to_env_str(value: list[str] | None) -> str | None:
    if value is None:
        return None

    return ",".join(value)


def float_to_env_str(value: float | None) -> str | None:
    if value is None:
        return None

    return str(value)
