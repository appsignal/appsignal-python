from unittest.mock import Mock

from appsignal.config import Options
from appsignal.opentelemetry import add_instrumentations, DefaultInstrumentation


def raise_module_not_found_error():
    raise ModuleNotFoundError()


def mock_adders() -> dict[DefaultInstrumentation, Mock]:
    return {
        "opentelemetry.instrumentation.celery": Mock(),
        "opentelemetry.instrumentation.jinja2": Mock(
            side_effect=raise_module_not_found_error
        ),
    }


def test_add_instrumentations():
    adders = mock_adders()
    config = Options()

    add_instrumentations(config, default_instrumentation_adders=adders)

    for adder in adders.values():
        adder.assert_called_once()


def test_add_instrumentations_disable_some_default_instrumentations():
    adders = mock_adders()
    config = Options(
        disable_default_instrumentations=["opentelemetry.instrumentation.celery"]
    )

    add_instrumentations(config, default_instrumentation_adders=adders)

    adders["opentelemetry.instrumentation.celery"].assert_not_called()
    adders["opentelemetry.instrumentation.jinja2"].assert_called_once()


def test_add_instrumentations_disable_all_default_instrumentations():
    adders = mock_adders()
    config = Options(disable_default_instrumentations=True)

    add_instrumentations(config, default_instrumentation_adders=adders)

    for adder in adders.values():
        adder.assert_not_called()