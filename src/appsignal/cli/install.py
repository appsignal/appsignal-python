from __future__ import annotations

import os

import requests

from .command import AppsignalCLICommand
from .demo import DemoCommand


INSTALL_FILE_TEMPLATE = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="{name}",
    push_api_key="{push_api_key}",
)
"""

INSTALL_FILE_NAME = "__appsignal__.py"


class InstallCommand(AppsignalCLICommand):
    """Generate Appsignal client integration code."""

    def run(self) -> int:
        # Make sure to show input prompts before the welcome text.
        self._name  # noqa: B018
        self._push_api_key  # noqa: B018

        print("👋 Welcome to the AppSignal for Python installer!")
        print()
        print("Reach us at support@appsignal.com for support")
        print("Documentation available at https://docs.appsignal.com/python")
        print()

        print()

        print("Validating API key")
        print()
        if self._validate_push_api_key():
            print("API key is valid!")
        else:
            print(f"API key {self._push_api_key} is not valid ")
            print("please get a new one on https://appsignal.com")
            return 1

        if self._should_write_file():
            print(f"Writing the {INSTALL_FILE_NAME} configuration file...")
            self._write_file()
            print()

            demo = DemoCommand(args=self.args)
            demo._name = self._name
            demo._push_api_key = self._push_api_key
            demo.run()

            if self._search_dependency("django"):
                self._django_installation()
            elif self._search_dependency("flask"):
                self._flask_installation()
            else:
                self._generic_installation()
        else:
            print("Nothing to do. Exiting...")

        return 0

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

    def _write_file(self) -> None:
        with open(INSTALL_FILE_NAME, "w") as f:
            file_contents = INSTALL_FILE_TEMPLATE.format(
                name=self._name,
                push_api_key=self._push_api_key,
            )

            f.write(file_contents)

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

        print("Django requires some manual configuration.")
        print("The __appsignal__ module needs to be imported in the manage.py file")
        print("and the appsignal.start() method needs to be called in the main method.")
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

        print("Flask requires some manual configuration.")
        print("The __appsignal__ module needs to be imported before Flask is imported")
        print("and the appsignal.start() method needs to be called right after.")
        print()
        print("Please refer to the documentation for more information:")
        print("https://docs.appsignal.com/python/instrumentations/flask.html")

    def _generic_installation(self) -> None:
        print("✅ Done! AppSignal for Python has now been installed.")
        print()
        print("To start AppSignal in your application, add the following code to your")
        print("application's entrypoint:")
        print()
        print("    from __appsignal__ import appsignal")
        print("    appsignal.start()")
        print()
        print("You can check a list of the supported integrations here:")
        print("https://docs.appsignal.com/python/instrumentations")

    def _add_dependency(self, dependency_name: str) -> None:
        requirement_file = self._requirements_file()
        if requirement_file:
            with open(requirement_file, "a") as f:
                f.write(f"{dependency_name}\n")

    def _validate_push_api_key(self) -> bool:
        endpoint = self._config.option("endpoint")
        url = f"{endpoint}/1/auth?api_key={self._push_api_key}"
        proxies = {}
        if self._config.option("http_proxy"):
            proxies["http"] = self._config.option("http_proxy")
            proxies["https"] = self._config.option("http_proxy")

        cert = self._config.option("ca_file_path")

        response = requests.get(url, proxies=proxies, verify=cert)
        return response.status_code == 200
