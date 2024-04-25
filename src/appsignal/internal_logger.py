from __future__ import annotations

import logging
import sys


_LOG_LEVEL_MAPPING: dict[str, int] = {
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "trace": logging.DEBUG,
}

_logger: logging.Logger | None = None


def _reset_logger() -> None:
    logger = logging.getLogger("appsignal")
    for handler in logger.handlers:
        logger.removeHandler(handler)

    global _logger
    _logger = None


def error(message: str) -> None:
    _log("error", message)


def warning(message: str) -> None:
    _log("warning", message)


def info(message: str) -> None:
    _log("info", message)


def debug(message: str) -> None:
    _log("debug", message)


def _log(level: str, message: str) -> None:
    global _logger

    if _logger is None:
        _logger = _configure_logger()

    _logger.log(_LOG_LEVEL_MAPPING[level], message)


def _configure_logger() -> logging.Logger:
    from .client import Client
    from .config import Config

    client_config = Client.config()
    config = client_config or Config({})
    level = config.option("log_level")

    logger = logging.getLogger("appsignal")
    logger.setLevel(_LOG_LEVEL_MAPPING[level])

    if config.option("log") == "file":
        log_file_path = config.log_file_path()
        if log_file_path:
            _configure_file_logger(logger, log_file_path)
        else:
            _configure_stdout_logger(logger)
    else:
        _configure_stdout_logger(logger)

    if client_config is None:
        logger.warning(
            "Internal logger used before initializing the AppSignal client; "
            "using default logger configuration."
        )

    return logger


def _configure_file_logger(logger: logging.Logger, log_file_path: str) -> None:
    handler = logging.FileHandler(log_file_path)
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s (process) #%(process)d][%(levelname)s] %(message)s",
            "%Y-%m-%dT%H:%M:%S",
        )
    )

    logger.addHandler(handler)


def _configure_stdout_logger(logger: logging.Logger) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s (process) #%(process)d][appsignal][%(levelname)s] "
            "%(message)s",
            "%Y-%m-%dT%H:%M:%S",
        )
    )

    logger.addHandler(handler)
