from __future__ import annotations

import json
from typing import Any


def dumps(objs: list[Any]) -> str:
    return "\n".join([json.dumps(line) for line in objs])


def loads(s: str) -> list[Any]:
    return [json.loads(line) for line in s.split("\n")]
