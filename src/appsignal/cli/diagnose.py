# ruff: noqa: E501

import json
import os
import platform
import urllib
from typing import Any, Optional

import requests

from appsignal.agent import Agent
from appsignal.config import Config
from appsignal.push_api_key_validator import PushApiKeyValidator

from ..__about__ import __version__
from .command import AppsignalCLICommand


class AgentReport:
    def __init__(self, report: dict) -> None:
        self.report = report

    def extension_loaded(self) -> str:
        return self.report["boot"]["started"]["result"]

    def configuration_valid(self) -> str:
        if self.report["config"]["valid"]["result"]:
            return "valid"
        return "invalid"

    def started(self) -> str:
        if self.report["boot"]["started"]["result"]:
            return "started"
        return "not started"

    def user_id(self) -> str:
        return self.report["host"]["uid"]["result"]

    def group_id(self) -> str:
        return self.report["host"]["gid"]["result"]

    def logger_started(self) -> str:
        if "logger" in self.report and self.report["logger"]["started"]["result"]:
            return "started"
        return "not started"

    def working_directory_user_id(self) -> bool:
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["uid"]["result"]
        )

    def working_directory_group_id(self) -> bool:
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["gid"]["result"]
        )

    def working_directory_permissions(self) -> bool:
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["mode"]["result"]
        )

    def lock_path(self) -> str:
        if "lock_path" in self.report and self.report["lock_path"]["created"]["result"]:
            return "writable"
        return "not writable"


class DiagnoseCommand(AppsignalCLICommand):
    def __init__(
        self, send_report: Optional[bool] = None, no_send_report: Optional[bool] = None
    ) -> None:
        agent = Agent()
        agent_json = json.loads(agent.diagnose())
        self.config = Config()
        self.send_report = send_report
        self.no_send_report = no_send_report
        self.agent_report = AgentReport(agent_json)

        self.report = {
            "agent": {
                "agent": {
                    "boot": agent_json["boot"],
                    "config": {
                        "valid": agent_json["config"]["valid"],
                    },
                    "host": agent_json["host"],
                    "lock_path": agent_json["lock_path"],
                    "logger": agent_json["logger"],
                    "working_directory_stat": agent_json["working_directory_stat"],
                }
            },
            "config": {
               "options": self.config.options,
               "sources": self.config.sources,
            },
            "host": {
                "architecture": platform.machine(),
                "heroku": os.environ.get("DYNO") is not None,
                "language_version": platform.python_version(),
                "os": platform.system().lower(),
                "os_distribution": self._os_distribution(),
                "root": False,
                "running_in_container": self.config.option("running_in_container")
                is not None,
            },
            "library": {
                "language": "python",
                "package_version": __version__,
                "agent_version": "91f1a7c",
                "extension_loaded": self.agent_report.extension_loaded(),
            },
            "paths": None,
            "process": None,
            "validation": {"push_api_key": self._validate_push_api_key()},
        }

    def run(self) -> int:
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

        if self.no_send_report:
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
        print(f'  Extension loaded: {library_report["extension_loaded"]}')

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
        print("  Extension tests")
        print(f"    Configuration: {self.agent_report.configuration_valid()}")
        print("  Agent tests")
        print(f"    Started: {self.agent_report.started()}")
        print(f"    Process user id: {self.agent_report.user_id()}")
        print(f"    Process user group id: {self.agent_report.group_id()}")
        print(f"    Configuration: {self.agent_report.configuration_valid()}")
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

    def _report_information(self) -> None:
        print("Diagnostics report")

    def _report_prompt(self) -> bool | None:
        print("  Do you want to send this diagnostics report to AppSignal?")
        print("  If you share this report you will be given a link to")
        print("  AppSignal.com to validate the report.")
        print("  You can also contact us at support@appsignal.com")
        print("  with your support token.")
        print()

        match input("  Send diagnostics report to AppSignal? (Y/n):   "):
            case "y" | "yes" | "":
                print("Transmitting diagnostics report")
                return True
            case "n" | "no":
                print("Not sending diagnostics information to AppSignal.")
                return False
            case _:
                self._report_prompt()
                return None

    def _send_diagnose_report(self) -> None:
        params = urllib.parse.urlencode(
            {
                "api_key": self.config.option("push_api_key"),
                "name": self.config.option("name"),
                "environment": self.config.option("environment"),
                "hostname": self.config.option("hostname") or "",
            }
        )

        endpoint = self.config.option("diagnose_endpoint")
        url = f"{endpoint}?{params}"

        response = requests.post(url, json={"diagnose": self.report})

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

    def _os_distribution(self) -> str:
        try:
            return platform.freedesktop_os_release()["NAME"]
        except OSError:
            return ""

    def _validate_push_api_key(self) -> str:
        match PushApiKeyValidator.validate(self.config):
            case "valid":
                return "valid"
            case "invalid":
                return "invalid"
            case value:
                return f"Failed to validate: {value}"
