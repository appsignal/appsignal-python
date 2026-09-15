from __future__ import annotations


# The one spelling a header name is compared and reported in: the name the
# OpenTelemetry semantic convention gives it, which is the header's own name
# lowercased, with its dashes kept. `Accept-Encoding` becomes `accept-encoding`.
#
# Two other spellings reach the collector for the same header. The
# OpenTelemetry SDK we build on writes an older spelling of the attribute,
# which replaced those dashes with underscores. And a configuration option
# naming the header is written by a person, who is as likely to write
# `Accept-Encoding`. The collector filters headers by name, so it only keeps
# the ones it is given under the name the convention gives them.
def normalize_header(name: str) -> str:
    return name.lower().replace("_", "-")


def normalize_headers(names: list[str] | None) -> list[str] | None:
    if names is None:
        return None

    return [normalize_header(name) for name in names]
