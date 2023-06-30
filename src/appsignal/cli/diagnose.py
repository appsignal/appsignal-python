import json
import os
import platform
import urllib
from argparse import ArgumentParser
from pathlib import Path

import requests

from appsignal.agent import Agent
from appsignal.config import Config

from ..__about__ import __version__
from .command import AppsignalCLICommand


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
        self.agent_report = json.loads(agent.diagnose())
        self.report = {
            "agent": None,
            "config": None,
            "host": None,
            "installation": None,
            "library": {
                "language": "python",
                "package_version": __version__,
                "agent_version": "91f1a7c",
                "extension_loaded": self.agent_report["boot"]["started"]["result"],
            },
            "paths": None,
            "process": None,
            "validation": None,
        }

        self._header()

        self._library_information()
        print()

        self._installation_information()
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
        print("AppSignal library")
        print("  Language: Python")
        print(f'  Package version: "{__version__}"')
        print(f'  Agent version: "91f1a7c"')
        print(f"  Extension loaded: {self.agent_report['boot']['started']['result']}")

    def _installation_information(self):
        print("Extension installation report")

    def _host_information(self):
        print("Host information")
        print(f"  Architecture: {platform.platform()}")
        print(f"  Operating System: {platform.system()} {platform.release()}")
        print(f"  Python version: {platform.python_version()}")
        print(f"  Root user: {os.getuid() == 0}")
        running_in_container = self.config.option("running_in_container")
        print(f"  Running in container: {running_in_container}")

    def _agent_information(self):
        print("Agent diagnostics")

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
