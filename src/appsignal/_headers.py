from __future__ import annotations


# The OpenTelemetry SDK writes header attribute names with underscores, where
# the semantic conventions the collector compares against use dashes.
def normalize_header(name: str) -> str:
    return name.lower().replace("_", "-")


def normalize_headers(names: list[str] | None) -> list[str] | None:
    if names is None:
        return None

    return [normalize_header(name) for name in names]
