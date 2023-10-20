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
