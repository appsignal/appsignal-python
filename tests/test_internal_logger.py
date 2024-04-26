import os
import re
from logging import DEBUG, ERROR, INFO, WARNING

from appsignal import internal_logger
from appsignal.client import Client


def test_logger_default_level():
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == INFO
    assert internal_logger._level == "info"


def test_logger_info_level():
    Client(log_level="info")
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == INFO
    assert internal_logger._level == "info"


def test_logger_error_level():
    Client(log_level="error")
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == ERROR
    assert internal_logger._level == "error"


def test_logger_warning_level():
    Client(log_level="warning")
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == WARNING
    assert internal_logger._level == "warning"


def test_logger_debug_level():
    Client(log_level="debug")
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == DEBUG
    assert internal_logger._level == "debug"


def test_logger_trace_level():
    Client(log_level="trace")
    internal_logger.info("trigger logger initialization")

    assert internal_logger._logger is not None
    assert internal_logger._logger.getEffectiveLevel() == DEBUG
    assert internal_logger._level == "trace"


def test_logger_trace_level_logs_trace(mocker):
    Client(log_level="trace")
    internal_logger.info("trigger logger initialization")

    mock = mocker.patch("appsignal.internal_logger._logger.log")
    internal_logger.trace("trace message")
    mock.assert_called_with(DEBUG, "trace message")
    internal_logger.debug("debug message")
    mock.assert_called_with(DEBUG, "debug message")


def test_logger_debug_level_does_not_log_trace(mocker):
    Client(log_level="debug")
    internal_logger.info("trigger logger initialization")

    mock = mocker.patch("appsignal.internal_logger._logger.log")
    internal_logger.trace("trace message")
    mock.assert_not_called()
    internal_logger.debug("debug message")
    mock.assert_called_with(DEBUG, "debug message")


def test_logger_file(tmp_path):
    log_path = tmp_path
    log_file_path = os.path.join(log_path, "appsignal.log")

    Client(log_path=log_path)
    internal_logger.info("test me")

    with open(log_file_path) as file:
        contents = file.read()

    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[INFO\] test me"
    )
    assert log_line_regex.search(contents)


def test_logger_stdout(capsys):
    Client(log="stdout")
    internal_logger.info("test me")

    captured = capsys.readouterr()
    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[appsignal\]"
        r"\[INFO\] test me"
    )
    assert log_line_regex.search(captured.out)


def test_logger_stdout_fallback(capsys, mocker):
    # Make any path appear unwritable so it will fall back to the STDOUT logger
    mocker.patch("os.access", return_value=False)

    Client(log="file", log_path=None)
    internal_logger.info("test me")

    captured = capsys.readouterr()
    log_line_regex = re.compile(
        r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \(process\) #\d+\]\[appsignal\]"
        r"\[INFO\] test me"
    )
    assert log_line_regex.search(captured.out)
