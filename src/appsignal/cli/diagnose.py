import platform
import os
import urllib
import requests
import json

from .command import AppsignalCLICommand
from appsignal.config import Config
from appsignal.agent import diagnose

from ..__about__ import __version__

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
    if self.report["logger"]["started"]["result"]:
        return "started"
    else:
        return "not started"

  def working_directory_user_id(self):
    return self.report["working_directory_stat"]["uid"]["result"]

  def working_directory_group_id(self):
    return self.report["working_directory_stat"]["gid"]["result"]

  def working_directory_permissions(self):
    return self.report["working_directory_stat"]["mode"]["result"]

  def lock_path(self):
    return self.report["lock_path"]["created"]["result"]


class DiagnoseCommand(AppsignalCLICommand):
    def __init__(self, send_report=None, no_send_report=None):
        self.config = Config()
        self.send_report = send_report
        self.no_send_report = no_send_report
        self.agent_report = AgentReport(json.loads(diagnose()))

        self.report = {
            "agent": None,
            "config": None,
            "host": {
                "architecture": platform.platform(),
                "heroku": os.environ.get("DYNO") is not None,
                "language_version": platform.python_version(),
                "os": platform.system().lower(),
                "os_distribution": "",
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
            "validation": None,
        }

    def run(self):
        self._header()

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
            self._send_diagnose_report()

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
        print(f'    Configuration: {self.agent_report.configuration_valid}')
        print("  Agent tests")
        print(f'    Started: {self.agent_report.started}')
        print(f'    Process user id: {self.agent_report.user_id}')
        print(f'    Process user group id: {self.agent_report.group_id}')
        print(f'    Configuration: {self.agent_report.configuration_valid}')
        print(f'    Logger: {self.agent_report.logger_started}')
        print(f'    Working directory user id: {self.agent_report.working_directory_user_id}')
        print(f'    Working directory user group id: {self.agent_report.working_directory_group_id}')
        print(f'    Working directory permissions: {self.agent_report.working_directory_permissions}')
        print(f'    Lock path: {self.agent_report.lock_path}')

    def _configuration_information(self):
        print("Configuration")

    def _validation_information(self):
        print("Validation")

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

        requests.post(url, json={"diagnose": self.report})
