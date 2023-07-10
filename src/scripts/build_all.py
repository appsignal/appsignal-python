from __future__ import annotations

import os
from runpy import run_path
from typing import Any


def run_relative(filename: str) -> dict[str, Any]:
    return run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))


TRIPLE_PLATFORM_TAG = run_relative("platform.py")["TRIPLE_PLATFORM_TAG"]

for triple in TRIPLE_PLATFORM_TAG:
    result = os.system(f"_APPSIGNAL_BUILD_TRIPLE={triple} hatch build -t wheel")
    if result != 0:
        break
