import platform
import os

from pathlib import Path

from .command import AppsignalCLICommand
from appsignal.config import Config

from ..__about__ import __version__

class DiagnoseCommand(AppsignalCLICommand):
    def __init__(self):
        self.config = Config()

    def run(self):
        self._header()

        self._library_information()
        print()

        self._host_information()
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

    def _host_information(self):
        print("Host information")
        print(f"  Architecture: {platform.platform()}")
        print(f"  Operating System: {platform.system()} {platform.release()}")
        print(f"  Python version: {platform.python_version()}")
        print(f"  Root user: {os.getuid() == 0}")
        running_in_container = self.config.option("running_in_container")
        print(f"  Running in container: {running_in_container)}")

    def _get_agent_version(self):


