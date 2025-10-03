from __future__ import annotations

from typing import List, cast
from unittest.mock import Mock

from appsignal.config import Config, Options
from appsignal.opentelemetry import add_instrumentations


def raise_module_not_found_error(_config: Config) -> None:
    raise ModuleNotFoundError


def mock_adders() -> dict[Config.DefaultInstrumentation, Mock]:
    return {
        "celery": Mock(),
        "jinja2": Mock(side_effect=raise_module_not_found_error),
    }


def test_add_instrumentations():
    adders = mock_adders()
    config = Config()

    add_instrumentations(config, _adders=adders)

    for adder in adders.values():
        adder.assert_called_once()


def test_add_instrumentations_disable_some_default_instrumentations():
    adders = mock_adders()
    config = Config(Options(disable_default_instrumentations=["celery"]))

    add_instrumentations(config, _adders=adders)

    adders["celery"].assert_not_called()
    adders["jinja2"].assert_called_once()


def test_disable_default_instrumentations_backwards_compatibility_prefix():
    adders = mock_adders()
    config = Config(
        Options(
            disable_default_instrumentations=cast(
                List[Config.DefaultInstrumentation],
                ["opentelemetry.instrumentation.celery"],
            )
        )
    )

    add_instrumentations(config, _adders=adders)

    adders["celery"].assert_not_called()
    adders["jinja2"].assert_called_once()


def test_add_instrumentations_disable_all_default_instrumentations():
    adders = mock_adders()
    config = Config(Options(disable_default_instrumentations=True))

    add_instrumentations(config, _adders=adders)

    for adder in adders.values():
        adder.assert_not_called()
