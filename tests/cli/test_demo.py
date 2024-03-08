from __future__ import annotations

import os
import shutil

from appsignal.cli.base import main
from appsignal.cli.install import INSTALL_FILE_TEMPLATE

from .utils import mock_input


def test_demo_with_valid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        (
            "Please enter the application environment (development/production): ",
            "development",
        ),
        ("Please enter your Push API key: ", "000"),
    ):
        assert main(["demo"]) == 0  # Successful run

    out, err = capfd.readouterr()
    assert "Sending example data to AppSignal..." in out


def test_demo_with_cli_options(mocker, capfd):
    assert (
        main(
            [
                "demo",
                "--application=Test",
                "--environment=development",
                "--push-api-key=000",
            ]
        )
        == 0  # Successful run
    )

    out, err = capfd.readouterr()
    assert "Sending example data to AppSignal..." in out


def test_demo_with_invalid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
        (
            "Please enter the application environment (development/production): ",
            "development",
        ),
        ("Please enter your Push API key: ", " "),  # Invalid empty key
    ):
        assert main(["demo"]) == 1  # Exit with error

    out, err = capfd.readouterr()
    assert "AppSignal not starting: no active config found." in out


def test_demo_with_config_file(request, mocker, capfd):
    test_dir = os.path.join(os.getcwd(), "tmp/dummy_project")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    # Change to test dir
    os.chdir(test_dir)
    # Add client file
    with open(os.path.join(test_dir, "__appsignal__.py"), "w") as f:
        file_contents = INSTALL_FILE_TEMPLATE.format(
            name="My app name",
            push_api_key="000",
        )
        f.write(file_contents)

    assert main(["demo"]) == 0  # Successful run

    # Change back to original dir
    os.chdir(request.config.invocation_params.dir)

    out, err = capfd.readouterr()
    assert "Sending example data to AppSignal..." in out
    assert "Starting AppSignal client for My app name..." in out


def test_demo_with_config_file_and_cli_options(request, mocker, capfd):
    test_dir = os.path.join(os.getcwd(), "tmp/dummy_project")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    # Change to test dir
    os.chdir(test_dir)
    # Add client file
    with open(os.path.join(test_dir, "__appsignal__.py"), "w") as f:
        file_contents = INSTALL_FILE_TEMPLATE.format(
            name="My app name",
            push_api_key="000",
        )
        f.write(file_contents)

    assert main(["demo", "--application=CLI app"]) == 0  # Successful run

    # Change back to original dir
    os.chdir(request.config.invocation_params.dir)

    out, err = capfd.readouterr()
    assert "Sending example data to AppSignal..." in out
    assert "Starting AppSignal client for CLI app..." in out


def test_demo_with_invalid_config_file(request, mocker, capfd):
    test_dir = os.path.join(os.getcwd(), "tmp/dummy_project")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    # Change to test dir
    os.chdir(test_dir)
    # Add invalid client file that doesn't assign the client to a variable
    # named `appsignal`
    with open(os.path.join(test_dir, "__appsignal__.py"), "w") as f:
        file_contents = """from appsignal import Appsignal

Appsignal(
    active=True,
    name="{name}",
    push_api_key="{push_api_key}",
)
"""
        f.write(file_contents)

    assert main(["demo", "--application=CLI app"]) == 1  # Exit with error

    # Change back to original dir
    os.chdir(request.config.invocation_params.dir)

    out, err = capfd.readouterr()
    assert "No `appsignal` variable found" in out
