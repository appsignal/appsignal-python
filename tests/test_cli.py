import builtins
from contextlib import contextmanager
from typing import cast
from unittest.mock import MagicMock


EXPECTED_FILE_CONTENTS = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="My app name",
    push_api_key="My push API key",
)
"""


@contextmanager
def mock_input(mocker, pairs):
    prompt_calls = [mocker.call(prompt) for (prompt, _) in pairs]
    answers = [answer for (_, answer) in pairs]

    mocker.patch("builtins.input", side_effect=answers)

    yield

    assert prompt_calls == cast(MagicMock, builtins.input).mock_calls


def mock_file_operations(mocker, file_exists=False):
    mocker.patch("os.path.exists", return_value=file_exists)
    mocker.patch("builtins.open")


def assert_wrote_file_contents(mocker):
    builtins_open = cast(MagicMock, builtins.open)
    assert mocker.call("__appsignal__.py", "w") in builtins_open.mock_calls
    assert (
        mocker.call().__enter__().write(EXPECTED_FILE_CONTENTS)
        in builtins_open.mock_calls
    )


def mock_validate_push_api_key_request(mocker, status_code=200):
    mock_request = mocker.patch("requests.get")
    mock_request.return_value = MagicMock(status_code=status_code)


def test_install_command_run(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", "My app name"),
            ("Please enter your Push API key: ", "My push API key"),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        InstallCommand().run()

    assert_wrote_file_contents(mocker)


def test_install_command_when_empty_value_ask_again(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", ""),
            ("Please enter the name of your application: ", "My app name"),
            ("Please enter your Push API key: ", ""),
            ("Please enter your Push API key: ", "My push API key"),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        InstallCommand().run()

    assert_wrote_file_contents(mocker)


def test_install_command_when_push_api_key_given(mocker):
    mock_file_operations(mocker)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", "My app name"),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        InstallCommand(push_api_key="My push API key").run()

    assert_wrote_file_contents(mocker)


def test_install_command_when_file_exists_overwrite(mocker):
    mock_file_operations(mocker, file_exists=True)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", "My app name"),
            ("Please enter your Push API key: ", "My push API key"),
            (
                "The __appsignal__.py file already exists."
                " Should it be overwritten? (y/N): ",
                "y",
            ),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        InstallCommand().run()

    assert_wrote_file_contents(mocker)


def test_install_command_when_file_exists_no_overwrite(mocker):
    mock_file_operations(mocker, file_exists=True)
    mock_validate_push_api_key_request(mocker)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", "My app name"),
            ("Please enter your Push API key: ", "My push API key"),
            (
                "The __appsignal__.py file already exists."
                " Should it be overwritten? (y/N): ",
                "n",
            ),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        InstallCommand().run()

    assert [] == cast(MagicMock, builtins.open).mock_calls


def test_install_comand_when_api_key_is_not_valid(mocker):
    mock_validate_push_api_key_request(mocker, status_code=401)

    with mock_input(
        mocker,
        [
            ("Please enter the name of your application: ", "My app name"),
        ],
    ):
        from appsignal.cli.install import InstallCommand

        assert InstallCommand(push_api_key="bad-push-api-key").run() == 1
