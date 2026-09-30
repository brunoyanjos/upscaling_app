from __future__ import annotations

import argparse

from upscaling_app.commands.distributions import (
    register_distribution_analysis_commands,
)
from upscaling_app.commands.experimental import (
    register_experimental_analysis_commands,
)
from upscaling_app.commands.ssdi import (
    register_ssdi_analysis_commands,
)
from upscaling_app.commands.ssmd import (
    register_ssmd_analysis_commands,
)


def register_analysis_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    analysis_parser = subparsers.add_parser(
        "analyze",
        help="Run statistical and experimental analyses.",
    )

    commands = analysis_parser.add_subparsers(
        dest="analysis_command",
        required=True,
    )

    register_experimental_analysis_commands(
        commands,
    )

    register_ssdi_analysis_commands(
        commands,
    )

    register_ssmd_analysis_commands(
        commands,
    )

    register_distribution_analysis_commands(
        commands,
    )
