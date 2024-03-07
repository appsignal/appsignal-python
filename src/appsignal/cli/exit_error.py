from __future__ import annotations


class ExitError(Exception):
    exit_code: int

    def __init__(self, exit_code: int) -> None:
        self.exit_code = exit_code
