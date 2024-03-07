from __future__ import annotations

import os
import shutil
from unittest.mock import MagicMock

from appsignal.cli.base import main
from appsignal.cli.install import INSTALL_FILE_TEMPLATE

from .utils import mock_input


EXPECTED_FILE_CONTENTS = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="My app name",
    # Please do not commit this key to your source control management system.
    # Move this to your app's security credentials or environment variables.
    # https://docs.appsignal.com/python/configuration/options.html#option-push_api_key
    push_api_key="My push API key",
)
"""


def mock_file_operations(mocker, file_exists: bool = False):
    mocker.patch("os.path.exists", return_value=file_exists)
    mocker.patch("appsignal.cli.install.open")


def assert_wrote_file_contents(mocker):
    from appsignal.cli import install

    builtins_open: MagicMock = install.open  # type: ignore[attr-defined]
    assert mocker.call("__appsignal__.py", "w") in builtins_open.mock_calls
    assert (
        mocker.call().__enter__().write(EXPECTED_FILE_CONTENTS)
        in builtins_open.mock_calls
    )


def assert_did_not_write_file_contents(mocker):
    from appsignal.cli import install

    builtins_open: MagicMock = install.open  # type: ignore[attr-defined]
    assert mocker.call("__appsignal__.py", "w") not in builtins_open.mock_calls
    assert (
        mocker.call().__enter__().write(EXPECTED_FILE_CONTENTS)
        not in builtins_open.mock_calls
    )


def assert_wrote_real_file_contents(test_dir, name, push_api_key):
    with open(os.path.join(test_dir, "__appsignal__.py")) as f:
        file_contents = INSTALL_FILE_TEMPLATE.format(
            name=name,
            push_api_key=push_api_key,
        )
        assert f.read() == file_contents


def mock_validate_push_api_key_request(mocker, status_code=200):
    mock_request = mocker.patch("requests.post")
    mock_request.return_value = MagicMock(status_code=status_code)


def test_install_command_run(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        ("Please enter your Push API key: ", "My push API key"),
    ):
        main(["install"])

    assert_wrote_file_contents(mocker)


def test_install_command_when_empty_value_ask_again(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", ""),
        ("Please enter the name of your application: ", "My app name"),
        ("Please enter your Push API key: ", ""),
        ("Please enter your Push API key: ", "My push API key"),
    ):
        main(["install"])

    assert_wrote_file_contents(mocker)


def test_install_command_when_push_api_key_given(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
    ):
        main(["install", "--push-api-key", "My push API key"])

    assert_wrote_file_contents(mocker)


def test_install_command_when_file_exists_overwrite(mocker, request):
    test_dir = os.path.join(os.getcwd(), "tmp/dummy_install_project")
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        ("Please enter your Push API key: ", "My push API key"),
        (
            "The __appsignal__.py file already exists."
            " Should it be overwritten? (y/N): ",
            "y",
        ),
    ):
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        os.makedirs(test_dir)
        # Add client file
        with open(os.path.join(test_dir, "__appsignal__.py"), "w") as f:
            file_contents = INSTALL_FILE_TEMPLATE.format(
                name="Existing app name",
                push_api_key="Existing Push API key",
            )
            f.write(file_contents)
        os.chdir(test_dir)

        main(["install"])

        # Change back to original dir
        os.chdir(request.config.invocation_params.dir)

    assert_wrote_real_file_contents(test_dir, "My app name", "My push API key")


def test_install_command_when_file_exists_no_overwrite(mocker):
    mock_file_operations(mocker, file_exists=True)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        ("Please enter your Push API key: ", "My push API key"),
        (
            "The __appsignal__.py file already exists."
            " Should it be overwritten? (y/N): ",
            "n",
        ),
    ):
        main(["install"])

    from appsignal.cli import install

    assert install.open.mock_calls == []  # type: ignore[attr-defined]


def test_install_command_when_invalid_api_key_ask_again(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker, status_code=401)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        ("Please enter your Push API key: ", "My push API key"),
        ("Please enter your Push API key: ", None),
    ):
        main(["install"])

    assert_did_not_write_file_contents(mocker)
