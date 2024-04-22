# ruff: noqa: E501

from __future__ import annotations

import json
import os
import platform
from argparse import ArgumentParser
from pathlib import Path
from sys import stderr
from typing import Any

from ..__about__ import __version__
from ..agent import Agent
from ..config import Config
from ..push_api_key_validator import PushApiKeyValidator
from ..transmitter import transmit
from .command import AppsignalCLICommand


class AgentReport:
    def __init__(self, report: dict) -> None:
        self.report = report

    def configuration_valid(self) -> str:
        if self.report["config"]["valid"]["result"]:
            return "valid"
        return "invalid"

    def configuration_error(self) -> str | None:
        if self.configuration_valid() == "invalid":
            return self.report["config"]["valid"]["error"]
        return None

    def started(self) -> str:
        if self.report["boot"]["started"]["result"]:
            return "started"
        return "not started"

    def user_id(self) -> str:
        return self.report["host"]["uid"]["result"]

    def group_id(self) -> str:
        return self.report["host"]["gid"]["result"]

    def running_in_container(self) -> str:
        return self.report["host"]["running_in_container"]["result"]

    def logger_started(self) -> str:
        if "logger" in self.report:
            if self.report["logger"]["started"]["result"]:
                return "started"
            return "not started"
        return "-"

    def working_directory_user_id(self) -> str:
        if "working_directory_stat" in self.report:
            return self.report["working_directory_stat"]["uid"]["result"]
        return "-"

    def working_directory_group_id(self) -> str:
        if "working_directory_stat" in self.report:
            return self.report["working_directory_stat"]["gid"]["result"]
        return "-"

    def working_directory_permissions(self) -> str:
        if "working_directory_stat" in self.report:
            return self.report["working_directory_stat"]["mode"]["result"]
        return "-"

    def lock_path(self) -> str:
        if "lock_path" in self.report:
            if self.report["lock_path"]["created"]["result"]:
                return "writable"
            return "not writable"
        return "-"


class PathsReport:
    def __init__(self, config: Config) -> None:
        self.config = config

    def paths(self) -> dict:
        log_file_path = self.config.log_file_path() or ""
        log_path = self.config.option("log_path") or os.path.dirname(log_file_path)

        return {
            "package_install_path": {
                "label": "Package install path",
                "path": str(Path(__file__).parents[3]),
            },
            "working_dir": {
                "label": "Current working directory",
                "path": os.getcwd() or "",
            },
            "log_dir_path": {
                "label": "Log directory",
                "path": log_path,
            },
            "appsignal.log": {
                "label": "AppSignal log",
                "path": log_file_path,
            },
        }

    def report(self) -> dict:
        paths = {}
        for key, config in self.paths().items():
            paths[key] = self._path_metadata(config["path"])

        return paths

    def _path_metadata(self, path: str) -> dict:
        info = {"path": path, "exists": self._file_exists(path)}
        if not info["exists"]:
            return info

        info["type"] = self._file_type(path)
        info["writable"] = os.access(path, os.W_OK)
        file_stat = os.stat(path)
        info["mode"] = str(file_stat.st_mode)
        info["ownership"] = {
            "gid": file_stat.st_gid,
            "uid": file_stat.st_uid,
        }
        if info["type"] == "file":
            info["content"] = self._read_last_two_mib(path)

        return info

    def _file_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def _file_type(self, path: str) -> str:
        if os.path.exists(path):
            if os.path.isfile(path):
                return "file"
            if os.path.isdir(path):
                return "directory"
        return ""

    def _read_last_two_mib(self, path: str) -> list[str]:
        two_mib = 2 * 1024 * 1024
        file_size = os.path.getsize(path)
        with open(path, "rb") as file:
            bytes_to_read = two_mib if two_mib < file_size else file_size
            file.seek(-bytes_to_read, os.SEEK_END)
            return file.read().decode("utf-8").strip().split("\n")


class DiagnoseCommand(AppsignalCLICommand):
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        parser.add_argument(
            "--send-report",
            action="store_true",
            help="Send the report to AppSignal",
        )
        parser.add_argument(
            "--no-send-report",
            action="store_true",
            help="Do not send the report to AppSignal",
        )

    def run(self) -> int:
        self.send_report = self.args.send_report
        self.no_send_report = self.args.no_send_report

        if self.send_report and self.no_send_report:
            print("Error: Cannot use --send-report and --no-send-report together.")
            return 1

        client = self._client_from_config_file()

        if client:
            self.config = client._config
        else:
            print(
                "Could not load the configuration from the `__appsignal__.py` "
                "configuration file. Some configuration options may be missing.",
                file=stderr,
            )
            self.config = Config()

        agent = Agent()
        agent_json = json.loads(agent.diagnose(self.config))
        self.agent_report = AgentReport(agent_json)
        self.paths_report = PathsReport(self.config)

        package_arch, package_platform = agent.architecture_and_platform()

        self.report = {
            "agent": {
                "agent": {
                    "boot": agent_json["boot"],
                    "config": {
                        "valid": agent_json["config"]["valid"],
                    },
                    "host": agent_json["host"],
                    "lock_path": agent_json.get("lock_path"),
                    "logger": agent_json.get("logger"),
                    "working_directory_stat": agent_json.get("working_directory_stat"),
                }
            },
            "config": {
                "options": self.config.options,
                "sources": self.config.sources,
            },
            "host": {
                "architecture": platform.machine(),
                "heroku": os.environ.get("DYNO") is not None,
                "running_in_container": self.agent_report.running_in_container(),
                "language_version": platform.python_version(),
                "os": platform.system().lower(),
                "os_distribution": self._os_distribution(),
                "root": os.getuid() == 0,
            },
            "library": {
                "language": "python",
                "package_version": __version__,
                "agent_version": str(agent.version(), "utf-8"),
                "package_architecture": package_arch,
                "package_platform": package_platform,
            },
            "paths": self.paths_report.report(),
            "process": {
                "uid": self._process_user(),
            },
            "validation": {"push_api_key": self._validate_push_api_key()},
        }

        self._header()
        print()

        self._library_information()
        print()

        self._host_information()
        print()

        self._agent_information()
        print()

        self._configuration_information()
        print()

        self._validation_information()
        print()

        self._paths_information()
        print()

        self._report_information()

        if self.send_report or (not self.no_send_report and self._report_prompt()):
            self._send_diagnose_report()
        elif self.no_send_report:
            print("Not sending report. (Specified with the --no-send-report option.)")

        return 0

    def _header(self) -> None:
        print("AppSignal diagnose")
        print("=" * 80)
        print("Use this information to debug your configuration.")
        print("More information is available on the documentation site.")
        print("https://docs.appsignal.com/")
        print("Send this output to support@appsignal.com if you need help.")
        print("=" * 80)

    def _library_information(self) -> None:
        library_report: Any = self.report["library"]
        print("AppSignal library")
        print("  Language: Python")
        print(f'  Package version: "{library_report["package_version"]}"')
        print(f'  Agent version: "{library_report["agent_version"]}"')
        print(f'  Package architecture: "{library_report["package_architecture"]}"')
        print(f'  Package platform: "{library_report["package_platform"]}"')

    def _host_information(self) -> None:
        host_report: Any = self.report["host"]
        print("Host information")
        print(f'  Architecture: "{host_report["architecture"]}"')
        print(f'  Operating System: "{host_report["os"]}"')
        print(f'  Python version: "{host_report["language_version"]}"')
        print(f'  Root user: {host_report["root"]}')
        print(f'  Running in container: {host_report["running_in_container"]}')

    def _agent_information(self) -> None:
        print("Agent diagnostics")
        print("  Agent tests")
        print(f"    Started: {self.agent_report.started()}")
        print(f"    Process user id: {self.agent_report.user_id()}")
        print(f"    Process user group id: {self.agent_report.group_id()}")
        print(f"    Configuration: {self.agent_report.configuration_valid()}")
        if self.agent_report.configuration_error():
            print(f"        Error: {self.agent_report.configuration_error()}")
        print(f"    Logger: {self.agent_report.logger_started()}")
        print(
            f"    Working directory user id: {self.agent_report.working_directory_user_id()}"
        )
        print(
            f"    Working directory user group id: {self.agent_report.working_directory_group_id()}"
        )
        print(
            f"    Working directory permissions: {self.agent_report.working_directory_permissions()}"
        )
        print(f"    Lock path: {self.agent_report.lock_path()}")

    def _configuration_information(self) -> None:
        print("Configuration")

        for key in self.config.options:
            print(f"  {key}: {self.config.options[key]!r}")  # type: ignore

        print()
        print("Read more about how the diagnose config output is rendered")
        print("https://docs.appsignal.com/python/command-line/diagnose.html")

    def _validation_information(self) -> None:
        validation_report: Any = self.report["validation"]
        print("Validation")
        print(f'  Validating Push API key: {validation_report["push_api_key"]}')

    def _paths_information(self) -> None:
        print("Paths")
        paths_report = self.paths_report
        report = paths_report.report()
        process_uid = self._process_user()
        for key, info in paths_report.paths().items():
            path_report = report[key]
            print(f"  {info['label']}")
            print(f"    Path: '{path_report['path']}'")

            if not path_report["exists"]:
                print("    Exists?: False")
                print()
                continue

            print(f"    Writable?: {path_report['writable']}")
            if process_uid:
                owned = path_report["ownership"]["uid"] == process_uid
            else:
                owned = "Unknown"
            owner = f"{owned} (file: {path_report['ownership']['uid']}, process: {process_uid})"
            print(f"    Ownership?: {owner}")

            if path_report.get("content"):
                print("    Contents (last 10 lines):")
                for line in path_report["content"][-10:]:
                    print(line.strip())
            else:
                print()

    def _report_information(self) -> None:
        print("Diagnostics report")

    def _report_prompt(self) -> bool | None:
        print("  Do you want to send this diagnostics report to AppSignal?")
        print("  If you share this report you will be given a link to")
        print("  AppSignal.com to validate the report.")
        print("  You can also contact us at support@appsignal.com")
        print("  with your support token.")
        print()

        send_report = input("  Send diagnostics report to AppSignal? (Y/n):   ").lower()

        if send_report in ["y", "yes", ""]:
            print("Transmitting diagnostics report")
            return True
        if send_report in ["n", "no"]:
            print("Not sending diagnostics information to AppSignal.")
            return False
        self._report_prompt()
        return None

    def _send_diagnose_report(self) -> None:
        url = self.config.option("diagnose_endpoint")

        response = transmit(url, json={"diagnose": self.report}, config=self.config)

        status = response.status_code
        if status == 200:
            token = response.json()["token"]
            print()
            print(f"  Your support token: {token}")
            print(f"  View this report:   https://appsignal.com/diagnose/{token}")
        else:
            print(
                "  Error: Something went wrong while submitting the report to AppSignal."
            )
            print(f"  Response code: {status}")
            print(f"  Response body: {response.text}")

    def _process_user(self) -> int:
        return os.getuid()

    def _os_distribution(self) -> str:
        try:
            return platform.freedesktop_os_release()["NAME"]
        # The platform.freedesktop_os_release is not available in all Python
        # versions that we support. That's why we catch AttributeError along with
        # OSError which is thrown when the host OS doesn't comply with freedesktop.
        except (OSError, AttributeError):
            return ""

    def _validate_push_api_key(self) -> str:
        api_key_validation = PushApiKeyValidator.validate(self.config)

        if api_key_validation == "valid":
            return "valid"
        if api_key_validation == "invalid":
            return "invalid"
        return f"Failed to validate: {api_key_validation}"
