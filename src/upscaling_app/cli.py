from __future__ import annotations

import argparse
import os
from importlib.metadata import PackageNotFoundError, version

import argcomplete

from upscaling_app.commands.analysis import (
    register_analysis_commands,
)
from upscaling_app.commands.database import (
    register_database_commands,
)
from upscaling_app.commands.ssdi import (
    register_ssdi_commands,
)
from upscaling_app.commands.ssmd import (
    register_ssmd_commands,
)


def _package_version() -> str:
    try:
        return version("upscaling-app")
    except PackageNotFoundError:
        return "0.1.0"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="upscaling",
        description=(
            "Scientific application for oil-dispersion modelling "
            "and statistical analysis."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_package_version()}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    register_database_commands(
        subparsers,
    )

    register_ssdi_commands(
        subparsers,
    )

    register_ssmd_commands(
        subparsers,
    )

    register_analysis_commands(
        subparsers,
    )

    return parser


def main() -> None:
    parser = create_parser()

    argcomplete.autocomplete(
        parser,
    )

    args = parser.parse_args()

    os.environ.setdefault(
        "XLA_PYTHON_CLIENT_PREALLOCATE",
        "false",
    )

    args.handler(
        args,
    )


if __name__ == "__main__":
    main()
