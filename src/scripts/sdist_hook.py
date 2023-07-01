from __future__ import annotations

from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """
        This occurs immediately before each build.

        Any modifications to the build data will be seen by the build target.
        """
        print(
            "It is not possible to build a source distribution package for "
            "this project, as it requires a platform-dependent binary."
        )
        print("Hint: you may wish to run `hatch run build:me` instead?")
        exit(1)
