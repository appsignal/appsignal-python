from __future__ import annotations

from argparse import ArgumentParser

from ..__about__ import __version__
from .command import AppsignalCLICommand


class VersionCommand(AppsignalCLICommand):
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        pass

    def run(self) -> int:
        print(__version__)
        return 0
