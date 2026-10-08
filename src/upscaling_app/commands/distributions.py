from __future__ import annotations

import argparse


def _run_distribution_fit(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.distributions.pipeline import (
        run_distribution_fit_workflow,
    )

    run_distribution_fit_workflow()


def _run_distribution_analysis(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.distributions.pipeline import (
        run_distribution_analysis_workflow,
    )

    run_distribution_analysis_workflow()


def register_distribution_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    distributions_parser = subparsers.add_parser(
        "distributions",
        help="Droplet-size distribution modelling.",
    )

    distribution_subparsers = distributions_parser.add_subparsers(
        dest="distribution_command",
        required=True,
    )

    fit_parser = distribution_subparsers.add_parser(
        "fit",
        help="Fit Rosin-Rammler parameters.",
    )

    fit_parser.set_defaults(
        handler=_run_distribution_fit,
    )


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
