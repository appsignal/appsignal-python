from abc import ABC, abstractmethod
import os
import json

from typing import Optional
from docopt import docopt

from .__about__ import __version__

from appsignal.client import Client
from opentelemetry import trace

DOC = """AppSignal for Python CLI.

Usage:
  appsignal install [--push-api-key=<key>]
  appsignal demo [--application=<app>] [--push-api-key=<key>]
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


class CLICommand(ABC):
    @abstractmethod
    def run(self) -> int:
        raise NotImplementedError


def command_for(arguments) -> CLICommand:
    if arguments["install"]:
        return InstallCommand(push_api_key=arguments["--push-api-key"])
    if arguments["demo"]:
        return DemoCommand(
            push_api_key=arguments["--push-api-key"],
            application=arguments["--application"],
        )
    else:
        raise NotImplementedError


INSTALL_FILE_TEMPLATE = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="{name}",
    push_api_key="{push_api_key}",
)
"""

INSTALL_FILE_NAME = "__appsignal__.py"


class AppsignalCLICommand(CLICommand):
    _push_api_key: Optional[str]
    _name: Optional[str]

    def _input_push_api_key(self):
        key = input("Please enter your Push API key: ")
        self._push_api_key = key
        if self._push_api_key == "":
            self._input_push_api_key()

    def _input_name(self):
        self._name = input("Please enter the name of your application: ")
        if self._name == "":
            self._input_name()


class InstallCommand(AppsignalCLICommand):
    def __init__(self, push_api_key=None):
        self._push_api_key = push_api_key
        self._name = None

    def run(self) -> int:
        print("👋 Welcome to the AppSignal for Python installer!")
        print()
        print("Reach us at support@appsignal.com for support")
        print("Documentation available at https://docs.appsignal.com/python")
        print()

        self._input_name()

        if self._push_api_key is None:
            self._input_push_api_key()

        print()

        if self._should_write_file():
            print(f"Writing the {INSTALL_FILE_NAME} configuration file...")
            self._write_file()
            print()

            DemoCommand(push_api_key=self._push_api_key, application=self._name).run()

            print("✅ Done! AppSignal for Python has now been installed.")
            print()
            print(
                "To start AppSignal in your application, add the following code to your"
            )
            print("application's entrypoint:")
            print()
            print("    from __appsignal__ import appsignal")
            print("    appsignal.start()")
            print()
        else:
            print("Nothing to do. Exiting...")

        return 0

    def _should_write_file(self):
        if os.path.exists(INSTALL_FILE_NAME):
            return self._input_should_overwrite_file()
        else:
            return True

    def _input_should_overwrite_file(self):
        response = input(
            f"The {INSTALL_FILE_NAME} file already exists."
            " Should it be overwritten? (y/N): "
        )
        if len(response) == 0 or response[0].lower() == "n":
            return False
        elif response[0].lower() == "y":
            return True
        else:
            print('Please answer "y" (yes) or "n" (no)')
            return self._input_should_overwrite_file()

    def _write_file(self):
        with open(INSTALL_FILE_NAME, "w") as f:
            file_contents = INSTALL_FILE_TEMPLATE.format(
                name=self._name,
                push_api_key=self._push_api_key,
            )

            f.write(file_contents)


class DemoCommand(AppsignalCLICommand):
    def __init__(self, push_api_key=None, application=None):
        self._push_api_key = push_api_key or os.environ.get("APPSIGNAL_PUSH_API_KEY")
        self._name = application or os.environ.get("APPSIGNAL_APP_NAME")

    def run(self) -> int:
        if self._push_api_key is None:
            self._input_push_api_key()

        if self._name is None:
            self._input_name()

        print()

        client = Client(
            active=True,
            name=self._name,
            push_api_key=self._push_api_key,
            log_level="trace",
        )

        print("Sending example data to AppSignal...")
        print(f"Starting AppSignal client for {self._name}...")
        client.start()

        tracer = trace.get_tracer(__name__)

        # Performance sample
        with tracer.start_as_current_span("GET /demo") as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute(
                "appsignal.request.parameters",
                json.dumps({"GET": {"id": 1}, "POST": {}}),
            )
            span.set_attribute(
                "otel.instrumentation_library.name",
                "opentelemetry.instrumentation.wsgi",
            )
            span.set_attribute(
                "demo_sample",
                True,
            )

        # Error sample
        with tracer.start_as_current_span("GET /demo") as span:
            span.set_attribute("http.method", "GET")
            span.set_attribute(
                "appsignal.request.parameters",
                json.dumps({"GET": {"id": 1}, "POST": {}}),
            )
            span.set_attribute(
                "demo_sample",
                True,
            )
            try:
                raise ValueError("Something went wrong")
            except ValueError as e:
                span.record_exception(e)

        return 0
