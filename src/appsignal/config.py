from __future__ import annotations

from typing import TypedDict


class Options(TypedDict, total=False):
    name: str
    environment: str
    push_api_key: str
    log_level: str
