import os
import pytest


@pytest.fixture(scope="function", autouse=True)
def reset_environment_between_tests():
    old_environ = dict(os.environ)

    yield

    os.environ.clear()
    os.environ.update(old_environ)
