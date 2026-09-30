from __future__ import annotations

import argparse


def _run_database_build(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.database.build import build_database

    build_database()


def register_database_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    database_parser = subparsers.add_parser(
        "database",
        help="Database operations.",
    )

    commands = database_parser.add_subparsers(
        dest="database_command",
        required=True,
    )

    build_parser = commands.add_parser(
        "build",
        help="Build normalized databases from raw data.",
    )

    build_parser.set_defaults(
        handler=_run_database_build,
    )
