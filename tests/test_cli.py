from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock

from appsignal.cli.base import main


EXPECTED_FILE_CONTENTS = """from appsignal import Appsignal

appsignal = Appsignal(
    active=True,
    name="My app name",
    push_api_key="My push API key",
)
"""


@contextmanager
def mock_input(mocker, *pairs: tuple[str, str]):
    prompt_calls = [mocker.call(prompt) for (prompt, _) in pairs]
    answers = [answer for (_, answer) in pairs]
    mock = mocker.patch("builtins.input", side_effect=answers)
    yield
    assert prompt_calls == mock.mock_calls


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


def mock_validate_push_api_key_request(mocker, status_code=200):
    mock_request = mocker.patch("requests.get")
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


def test_install_command_when_file_exists_overwrite(mocker):
    mock_file_operations(mocker, file_exists=True)
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
        main(["install"])

    assert_wrote_file_contents(mocker)


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


def test_install_comand_when_api_key_is_not_valid(mocker):
    mock_validate_push_api_key_request(mocker, status_code=401)

    with mock_input(
        mocker,
        ("Please enter the name of your application: ", "My app name"),
    ):
        assert main(["install", "--push-api-key=bad-push-api-key"]) == 1
