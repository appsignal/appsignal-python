from __future__ import annotations

from contextlib import contextmanager

from appsignal.cli.base import main


@contextmanager
def mock_input(mocker, *pairs: tuple[str, str]):
    prompt_calls = [mocker.call(prompt) for (prompt, _) in pairs]
    answers = [answer for (_, answer) in pairs]
    mock = mocker.patch("builtins.input", side_effect=answers)
    yield
    assert prompt_calls == mock.mock_calls


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
    assert out.find("Sending example data to AppSignal...") > -1


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
    assert out.find("Sending example data to AppSignal...") > -1


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
    assert out.find("AppSignal not starting: no active config found.") > -1
