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


def test_diagnose_with_valid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("  Send diagnostics report to AppSignal? (Y/n):   ", "N"),
    ):
        main(["diagnose"])

    out, err = capfd.readouterr()
    assert out.find("AppSignal diagnose") > -1


def test_diagnose_with_cli_options(mocker, capfd):
    main(["diagnose", "--no-send-report"])

    out, err = capfd.readouterr()
    assert out.find("AppSignal diagnose") > -1
    assert (
        out.find("Not sending report. (Specified with the --no-send-report option.)")
        > -1
    )


def test_diagnose_with_invalid_send_report_cli_options(mocker, capfd):
    assert main(["diagnose", "--send-report", "--no-send-report"]) == 1

    out, err = capfd.readouterr()
    assert (
        out.find("Error: Cannot use --send-report and --no-send-report together.") > -1
    )


def test_diagnose_with_invalid_config(mocker, capfd):
    with mock_input(
        mocker,
        ("  Send diagnostics report to AppSignal? (Y/n):   ", "N"),
    ):
        main(["diagnose"])

    out, err = capfd.readouterr()
    assert out.find("AppSignal diagnose") > -1
