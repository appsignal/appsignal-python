from __future__ import annotations

import sys
from argparse import ArgumentParser
from typing import Mapping, NoReturn

from .command import AppsignalCLICommand
from .demo import DemoCommand
from .install import InstallCommand
from .version import VersionCommand


COMMANDS: Mapping[str, type[AppsignalCLICommand]] = {
    "demo": DemoCommand,
    "install": InstallCommand,
    "version": VersionCommand,
}


def run() -> NoReturn:
    """The entry point for CLI."""
    sys.exit(main(sys.argv[1:]))


def main(argv: list[str]) -> int:
    parser = ArgumentParser("appsignal", description="AppSignal for Python CLI.")
    subparsers = parser.add_subparsers()
    parser.set_defaults(cmd=None)

    cmd_class: type[AppsignalCLICommand]
    for name, cmd_class in COMMANDS.items():
        subparser = subparsers.add_parser(name=name, help=cmd_class.__doc__)
        subparser.set_defaults(cmd=cmd_class)
        cmd_class.init_parser(subparser)
    args = parser.parse_args(argv)

    cmd_class = args.cmd
    if cmd_class is None:
        parser.print_help()
        return 1
    cmd = cmd_class(args=args)
    try:
        return cmd.run()
    except KeyboardInterrupt:
        return 0
