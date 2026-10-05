from __future__ import annotations

import argparse


def _run_distribution_analysis(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.distributions.pipeline import (
        run_distribution_analysis,
    )

    result = run_distribution_analysis()


def register_distribution_analysis_commands(
    analysis_subparsers: argparse._SubParsersAction,
) -> None:
    distributions_parser = analysis_subparsers.add_parser(
        "distributions",
        help="Analyze measured droplet-size distributions.",
    )

    distributions_parser.set_defaults(
        handler=_run_distribution_analysis,
    )
