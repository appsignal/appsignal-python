from docopt import docopt

from ..__about__ import __version__
from .command import AppsignalCLICommand
from .demo import DemoCommand
from .install import InstallCommand
from .diagnose import DiagnoseCommand


DOC = """AppSignal for Python CLI.

Usage:
  appsignal install [--push-api-key=<key>]
  appsignal demo [--application=<app>] [--push-api-key=<key>]
  appsignal diagnose [--send-report] [--no-send-report]
  appsignal (-h | --help)
  appsignal --version

Options:
  -h --help             Show this screen and exit.
  --version             Show version number and exit.
  --push-api-key=<key>  Push API Key to use for the installation and the demo.
  --application=<app>   Application name to use for the demo.
"""


def run():
    try:
        version = f"AppSignal for Python v{__version__}"

        arguments = docopt(DOC, version=version)

        return command_for(arguments).run()
    except KeyboardInterrupt:
        return 0


def command_for(arguments) -> AppsignalCLICommand:
    if arguments["install"]:
        return InstallCommand(push_api_key=arguments["--push-api-key"])
    if arguments["demo"]:
        return DemoCommand(
            push_api_key=arguments["--push-api-key"],
            application=arguments["--application"],
        )
    if arguments["diagnose"]:
        return DiagnoseCommand(
            send_report=arguments["--send-report"],
            no_send_report=arguments["--no-send-report"],
        )
    else:
        raise NotImplementedError
