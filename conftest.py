from __future__ import annotations

import logging
import os
import platform
import tempfile

import pytest

from appsignal.agent import _reset_agent_active


@pytest.fixture(scope="function", autouse=True)
def reset_environment_between_tests():
    old_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture(scope="function", autouse=True)
def remove_logging_handlers_after_tests():
    yield

    logger = logging.getLogger("appsignal")
    for handler in logger.handlers:
        logger.removeHandler(handler)


@pytest.fixture(scope="function", autouse=True)
def reset_agent_active_state():
    _reset_agent_active()


@pytest.fixture(scope="function", autouse=True)
def stop_agent():
    tmp_path = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()
    working_dir = os.path.join(tmp_path, "appsignal")
    if os.path.isdir(working_dir):
        os.system(r"rm -rf {working_dir}")

    yield
