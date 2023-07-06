import json
import os
import platform
import urllib
from argparse import ArgumentParser
from pathlib import Path

import requests

from appsignal.agent import Agent
from appsignal.config import Config
from appsignal.push_api_key_validator import PushApiKeyValidator

from ..__about__ import __version__
from .command import AppsignalCLICommand


class AgentReport:
    def __init__(self, report):
        self.report = report

    def extension_loaded(self):
        return self.report["boot"]["started"]["result"]

    def configuration_valid(self):
        if self.report["config"]["valid"]["result"]:
            return "valid"
        else:
            return "invalid"

    def started(self):
        if self.report["boot"]["started"]["result"]:
            return "started"
        else:
            return "not started"

    def user_id(self):
        return self.report["host"]["uid"]["result"]

    def group_id(self):
        return self.report["host"]["gid"]["result"]

    def logger_started(self):
        if "logger" in self.report and self.report["logger"]["started"]["result"]:
            return "started"
        else:
            return "not started"

    def working_directory_user_id(self):
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["uid"]["result"]
        )

    def working_directory_group_id(self):
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["gid"]["result"]
        )

    def working_directory_permissions(self):
        return (
            "working_directory_stat" in self.report
            and self.report["working_directory_stat"]["mode"]["result"]
        )

    def lock_path(self):
        if "lock_path" in self.report and self.report["lock_path"]["created"]["result"]:
            return "writable"
        else:
            return "not writable"

    def lock_path(self):
        if self.report["lock_path"]["created"]["result"]:
            return "writable"
        else:
            return "not writable"


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

    def run(self):
        agent = Agent()
        self.config = Config()
        self.send_report = self.args.send_report
        self.no_send_report = self.args.no_send_report
        self.agent_report = AgentReport(json.loads(agent.diagnose()))
        self.report = {
            "agent": None,
            "config": None,
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
        print()

        if self.send_report or (not self.no_send_report and self._report_prompt()):
            token = self._send_diagnose_report()
            print(f'  Your support token: {token}')
            print(f'  View this report:   https://appsignal.com/diagnose/{token}')

        if self.no_send_report:
            print("Not sending report. (Specified with the --no-send-report option.)")

    def _header(self):
        print("AppSignal diagnose")
        print("=" * 80)
        print("Use this information to debug your configuration.")
        print("More information is available on the documentation site.")
        print("https://docs.appsignal.com/")
        print("Send this output to support@appsignal.com if you need help.")
        print("=" * 80)

    def _library_information(self):
        library_report = self.report["library"]
        print("AppSignal library")
        print("  Language: Python")
        print(f'  Package version: "{library_report["package_version"]}"')
        print(f'  Agent version: "{library_report["agent_version"]}"')
        print(f'  Extension loaded: {library_report["extension_loaded"]}')

    def _host_information(self):
        host_report = self.report["host"]
        print("Host information")
        print(f'  Architecture: "{host_report["architecture"]}"')
        print(f'  Operating System: "{host_report["os"]}"')
        print(f'  Python version: "{host_report["language_version"]}"')
        print(f'  Root user: {host_report["root"]}')
        print(f'  Running in container: {host_report["running_in_container"]}')

    def _agent_information(self):
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

    def _configuration_information(self):
        print("Configuration")

        for key in self.config.options:
            print(f"  {key}: {repr(self.config.options[key])}")

        print()
        print("Read more about how the diagnose config output is rendered")
        print("https://docs.appsignal.com/python/command-line/diagnose.html")

    def _validation_information(self):
        validation_report = self.report["validation"]
        print("Validation")
        print(f'  Validating Push API key: {validation_report["push_api_key"]}')

    def _paths_information(self):
        print("Paths")

    def _report_information(self):
        print("Diagnostics report")

    def _report_prompt(self):
        match input("  Send diagnostics report to AppSignal? (Y/n):"):
            case "y" | "yes" | "":
                return True
            case "n" | "no":
                return False
            case _:
                report_prompt()

    def _send_diagnose_report(self):
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
        return response.json()["token"]

    def _os_distribution(self):
        try:
            return platform.freedesktop_os_release()
        except OSError:
            return ""

    def _validate_push_api_key(self):
        match PushApiKeyValidator.validate(self.config):
            case "valid":
                return "valid"
            case "invalid":
                return "invalid"
            case value:
                return f"Failed to validate: {value}"
