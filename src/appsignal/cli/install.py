from __future__ import annotations

import os
from argparse import ArgumentParser

from ..client import Client
from ..config import Options
from .command import AppsignalCLICommand
from .demo import Demo


INSTALL_FILE_TEMPLATE = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
{options})
"""

INSTALL_FILE_OPTION_COMMENTS = {
    "push_api_key": [
        "Please do not commit this key to your source control management system.",
        "Move this to your app's security credentials or environment variables.",
        "https://docs.appsignal.com/python/configuration/options.html"
        "#option-push_api_key",
    ],
}

COLLECTOR_URL = (
    "https://appsignal.com/redirect-to/organization?to=admin/hosted_collectors"
)

INSTALL_FILE_NAME = "__appsignal__.py"

WARNING_EMOJI = "\u26A0\ufe0f"


def install_file_contents(options: Options) -> str:
    lines: list[str] = []
    for key, value in options.items():
        lines.extend(
            f"    # {comment}\n"
            for comment in INSTALL_FILE_OPTION_COMMENTS.get(key, [])
        )
        lines.append(f'    {key}="{value}",\n')
    return INSTALL_FILE_TEMPLATE.format(options="".join(lines))


class InstallCommand(AppsignalCLICommand):
    """Generate Appsignal client integration code."""

    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        AppsignalCLICommand._application_argument(parser)
        AppsignalCLICommand._push_api_key_argument(parser)

    def run(self) -> int:
        options = Options()

        print("👋 Welcome to the AppSignal for Python installer!")
        print()
        print("Reach us at support@appsignal.com for support")
        print("Documentation available at https://docs.appsignal.com/python")
        print()

        options["name"] = self._name()
        options["push_api_key"] = self._valid_push_api_key()

        print()

        collector_endpoint = self._collector_endpoint()
        if collector_endpoint:
            options["collector_endpoint"] = collector_endpoint
            options["service_name"] = self._service_name()
            print()

        if self._should_write_file():
            print(f"Writing the {INSTALL_FILE_NAME} configuration file...")
            self._write_file(options)
            print()
            print()

            client = Client(
                active=True,
                name=options["name"],
                push_api_key=options["push_api_key"],
            )
            client.start()
            Demo.transmit()

            if self._search_dependency("django"):
                self._django_installation()
            elif self._search_dependency("flask"):
                self._flask_installation()
            else:
                self._generic_installation()
        else:
            print("Nothing to do. Exiting...")

        return 0

    def _collector_endpoint(self) -> str | None:
        while True:
            endpoint = input(
                f"Please enter your collector endpoint (create one at {COLLECTOR_URL}): "
            )
            if endpoint:
                return endpoint
            if self._input_should_continue_without_collector():
                return None

    def _input_should_continue_without_collector(self) -> bool:
        response = input(
            "Are you sure? Without a collector, logging and distributed tracing"
            " won't work. Continue without one? (y/N): "
        )
        if len(response) == 0 or response[0].lower() == "n":
            return False
        if response[0].lower() == "y":
            return True
        print('Please answer "y" (yes) or "n" (no)')
        return self._input_should_continue_without_collector()

    def _service_name(self) -> str:
        name = ""
        while not name:
            name = input(
                "Please enter the name of this service"
                " (such as web-server or background-worker): "
            )
        return name

    def _should_write_file(self) -> bool:
        if os.path.exists(INSTALL_FILE_NAME):
            return self._input_should_overwrite_file()
        return True

    def _input_should_overwrite_file(self) -> bool:
        response = input(
            f"The {INSTALL_FILE_NAME} file already exists."
            " Should it be overwritten? (y/N): "
        )
        if len(response) == 0 or response[0].lower() == "n":
            return False
        if response[0].lower() == "y":
            return True
        print('Please answer "y" (yes) or "n" (no)')
        return self._input_should_overwrite_file()

    def _write_file(self, options: Options) -> None:
        with open(INSTALL_FILE_NAME, "w") as f:
            f.write(install_file_contents(options))

    def _requirements_file(self) -> str | None:
        current_dir = os.getcwd()
        for _root, _dirs, files in os.walk(current_dir):
            for file in files:
                if file.endswith("requirements.txt"):
                    return file
        return None

    def _search_dependency(self, dependency_name: str) -> bool:
        requirement_file = self._requirements_file()
        if requirement_file:
            with open(requirement_file) as f:
                for line in f.readlines():
                    return line.startswith(dependency_name)

        return False

    def _django_installation(self) -> None:
        print("We've detected that you're using Django.")
        print()

        if not self._search_dependency("opentelemetry-instrumentation-django"):
            print("Adding the Django instrumentation to your requirements.txt file")
            print()
            self._add_dependency("opentelemetry-instrumentation-django")

        print(f"{WARNING_EMOJI} Django requires some manual configuration.")
        print(
            "AppSignal needs to be imported and started at your Django application's "
            "entry points."
        )
        print()
        print("Please refer to the documentation for more information:")
        print("https://docs.appsignal.com/python/instrumentations/django.html")

    def _flask_installation(self) -> None:
        print("We've detected that you're using Flask.")
        print()

        if not self._search_dependency("opentelemetry-instrumentation-flask"):
            print("Adding the Flask instrumentation to your requirements.txt file")
            print()
            self._add_dependency("opentelemetry-instrumentation-flask")

        print(f"{WARNING_EMOJI} Flask requires some manual configuration.")
        print(
            "AppSignal needs to be imported and initialized before Flask is imported."
        )
        print()
        print("    import appsignal")
        print("    appsignal.start()")
        print("    import flask")
        print()
        print("Please refer to the documentation for more information:")
        print("https://docs.appsignal.com/python/instrumentations/flask.html")

    def _generic_installation(self) -> None:
        print("✅ Done! AppSignal for Python has now been installed.")
        print()
        print(f"{WARNING_EMOJI} Some manual configuration might be required.")
        print("To start AppSignal in your application, add the following code to your")
        print("application's entrypoint:")
        print()
        print("    import appsignal")
        print("    appsignal.start()")
        print()
        print("You can check a list of the supported integrations here:")
        print("https://docs.appsignal.com/python/instrumentations")

    def _add_dependency(self, dependency_name: str) -> None:
        requirement_file = self._requirements_file()
        if requirement_file:
            with open(requirement_file, "a") as f:
                f.write(f"{dependency_name}\n")
