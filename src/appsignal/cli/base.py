from __future__ import annotations

import sys
from argparse import ArgumentParser
from typing import Mapping, NoReturn

from .command import AppsignalCLICommand
from .demo import DemoCommand
from .diagnose import DiagnoseCommand
from .install import InstallCommand
from .version import VersionCommand


COMMANDS: Mapping[str, type[AppsignalCLICommand]] = {
    "demo": DemoCommand,
    "install": InstallCommand,
    "version": VersionCommand,
    "diagnose": DiagnoseCommand,
}


def run() -> NoReturn:
    print(
        "The AppSignal for Python integration is now published as the "
        "`appsignal` package on PyPI. Update your project's dependencies "
        "(e.g. requirements.txt) replacing the `appsignal-beta` package "
        "with the `appsignal` package.",
        file=sys.stderr,
    )

    """The entry point for CLI."""
    sys.exit(main(sys.argv[1:]))


def main(argv: list[str]) -> int:
    parser = ArgumentParser("appsignal", description="AppSignal for Python CLI.")
    _register_commands(parser)
    args = parser.parse_args(argv)
    cmd_class: type[AppsignalCLICommand] | None
    cmd_class = args.cmd
    if cmd_class is None:
        parser.print_help()
        return 1
    cmd = cmd_class(args=args)
    try:
        return cmd.run()
    except KeyboardInterrupt:
        return 0


def _register_commands(parser: ArgumentParser) -> None:
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)
    cmd_class: type[AppsignalCLICommand]
    for name, cmd_class in COMMANDS.items():
        subparser = subparsers.add_parser(name=name, help=cmd_class.__doc__)
        subparser.set_defaults(cmd=cmd_class)
        cmd_class.init_parser(subparser)
