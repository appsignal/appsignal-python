import os
import platform
from argparse import ArgumentParser
from pathlib import Path

from appsignal.config import Config

from ..__about__ import __version__
from .command import AppsignalCLICommand


class DiagnoseCommand(AppsignalCLICommand):
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        pass

    def run(self):
        self.config = Config()

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
        print(f"  Package version: {__version__}")
        print(f"  Agent version: ")

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
      print(f"Configuration")

    def _validation_information(self):
      print(f"Validation")

    def _paths_information(self):
      print(f"Paths")

    def _report_information(self):
      print(f"Diagnostics report")
