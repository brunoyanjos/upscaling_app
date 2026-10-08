from __future__ import annotations

import argparse


def _run_experimental_summary(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.experimental.summary.pipeline import (
        run_experimental_summary_workflow,
    )

    run_experimental_summary_workflow(
        kind=args.kind,
    )


def _run_experimental_treatment_effect(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.experimental.treatment_effect.pipeline import (
        run_treatment_effect_workflow,
    )

    run_treatment_effect_workflow()


def _run_experimental_ssdi(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.experimental.ssdi.pipeline import (
        run_ssdi_experimental_workflow,
    )

    run_ssdi_experimental_workflow()


def _run_experimental_ssmd(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.experimental.ssmd.pipeline import (
        run_ssmd_experimental_workflow,
    )

    run_ssmd_experimental_workflow()


def _run_experimental_distributions(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.experimental.distributions.pipeline import (
        run_distribution_experimental_workflow,
    )

    run_distribution_experimental_workflow()


def register_experimental_analysis_commands(
    analysis_subparsers: argparse._SubParsersAction,
) -> None:
    experimental_parser = analysis_subparsers.add_parser(
        "experimental",
        help="Analyze measured experimental data.",
    )

    commands = experimental_parser.add_subparsers(
        dest="experimental_command",
        required=True,
    )

    summary_parser = commands.add_parser(
        "summary",
        help="Summarize experimental coverage and completeness.",
    )

    summary_parser.add_argument(
        "--kind",
        choices=[
            "all",
            "untreated",
            "ssdi",
            "ssmd",
        ],
        default="all",
        help="Experimental population to summarize.",
    )

    summary_parser.set_defaults(
        handler=_run_experimental_summary,
    )

    treatment_parser = commands.add_parser(
        "treatment-effect",
        help="Analyze D50 reduction relative to untreated conditions.",
    )

    treatment_parser.set_defaults(
        handler=_run_experimental_treatment_effect,
    )

    ssdi_parser = commands.add_parser(
        "ssdi",
        help="Analyze SSDI experimental relationships.",
    )

    ssdi_parser.set_defaults(
        handler=_run_experimental_ssdi,
    )

    ssmd_parser = commands.add_parser(
        "ssmd",
        help="Analyze SSMD experimental relationships.",
    )

    ssmd_parser.set_defaults(
        handler=_run_experimental_ssmd,
    )

    distributions_parser = commands.add_parser(
        "distributions",
        help="Analyze experimental droplet-size distributions.",
    )

    distributions_parser.set_defaults(
        handler=_run_experimental_distributions,
    )
