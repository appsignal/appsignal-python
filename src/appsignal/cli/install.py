import requests
import os

from .command import AppsignalCLICommand
from .demo import DemoCommand

from appsignal.config import Config

INSTALL_FILE_TEMPLATE = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="{name}",
    push_api_key="{push_api_key}",
)
"""

INSTALL_FILE_NAME = "__appsignal__.py"


class InstallCommand(AppsignalCLICommand):
    def __init__(self, push_api_key=None):
        self._push_api_key = push_api_key
        self._name = None
        self._config = Config()

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

            DemoCommand(push_api_key=self._push_api_key, application=self._name).run()

            if self._search_dependency("django"):
                self._django_installation()
            elif self._search_dependency("flask"):
                self._flask_installation()
            else:
                self._generic_installation()
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

    def _requirements_file(self):
        current_dir = os.getcwd()
        for _root, _dirs, files in os.walk(current_dir):
            for file in files:
                if file.endswith("requirements.txt"):
                    return file
        return None

    def _search_dependency(self, dependency_name):
        requirement_file = self._requirements_file()
        if requirement_file:
            with open(requirement_file, "r") as f:
                for line in f.readlines():
                    return line.startswith(dependency_name)

        return False

    def _django_installation(self):
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

    def _flask_installation(self):
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

    def _generic_installation(self):
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

    def _add_dependency(self, dependency_name):
        requirement_file = self._requirements_file()
        if requirement_file:
            with open(requirement_file, "a") as f:
                f.write(f"{dependency_name}\n")

    def _validate_push_api_key(self):
        endpoint = self._config.option("endpoint")
        url = f"{endpoint}/1/auth?api_key={self._push_api_key}"
        proxies = {}
        if self._config.option("http_proxy"):
            proxies["http"] = self._config.option("http_proxy")
            proxies["https"] = self._config.option("http_proxy")

        cert = self._config.option("ca_file_path")

        response = requests.get(url, proxies=proxies, verify=cert)
        return response.status_code == 200
