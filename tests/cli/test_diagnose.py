from __future__ import annotations

import os
import shutil

from appsignal.cli.base import main
from appsignal.cli.install import INSTALL_FILE_TEMPLATE

from .utils import mock_input


def test_diagnose_with_valid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("  Send diagnostics report to AppSignal? (Y/n):   ", "N"),
    ):
        main(["diagnose"])

    out, err = capfd.readouterr()
    assert "AppSignal diagnose" in out
    assert "Agent tests\n    Started: started" in out
    # Check if the agent picks up the config. This is the first check that
    # would fail.
    assert 'RequiredEnvVarNotPresent("_APPSIGNAL_APP_ENV")' not in out
    # TODO: fix in https://github.com/appsignal/appsignal-python/issues/142
    # assert out.find("Configuration: invalid") == -1
    # assert out.find("RequiredEnvVarNotPresent(\"_APPSIGNAL_PUSH_API_KEY\")") == -1


def test_diagnose_with_cli_options(mocker, capfd):
    main(["diagnose", "--no-send-report"])

    out, err = capfd.readouterr()
    assert "AppSignal diagnose" in out
    assert "Not sending report. (Specified with the --no-send-report option.)" in out


def test_diagnose_with_invalid_send_report_cli_options(mocker, capfd):
    assert main(["diagnose", "--send-report", "--no-send-report"]) == 1

    out, err = capfd.readouterr()
    assert "Error: Cannot use --send-report and --no-send-report together." in out


def test_diagnose_with_invalid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("  Send diagnostics report to AppSignal? (Y/n):   ", "N"),
    ):
        main(["diagnose"])

    out, err = capfd.readouterr()
    assert "AppSignal diagnose" in out

    # Check if the agent tests fail. This is the first check that would fail.
    assert 'RequiredEnvVarNotPresent("_APPSIGNAL_PUSH_API_KEY")' in out


def test_diagnose_with_config_file(request, mocker, capfd):
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

    assert main(["diagnose", "--no-send-report"]) == 0  # Successful run

    # Change back to original dir
    os.chdir(request.config.invocation_params.dir)

    out, err = capfd.readouterr()
    assert "name: 'My app name'" in out
    assert "push_api_key: '000'" in out


def test_diagnose_with_invalid_config_file(request, mocker, capfd):
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

    assert main(["diagnose"]) == 1  # Exit with error

    # Change back to original dir
    os.chdir(request.config.invocation_params.dir)

    out, err = capfd.readouterr()
    assert "No `appsignal` variable found" in out


def test_diagnose_with_missing_paths(mocker, capfd):
    mocker.patch("appsignal.cli.diagnose.PathsReport._file_exists", return_value=False)
    assert main(["diagnose", "--no-send-report"]) == 0

    out, err = capfd.readouterr()
    assert "Exists?: False" in out
