import os
import logging
import pytest


@pytest.fixture(scope="function", autouse=True)
def reset_environment_between_tests():
    old_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(old_environ)

    logger = logging.getLogger("appsignal")
    for handler in logger.handlers:
        logger.removeHandler(handler)
