from __future__ import annotations

import argparse

from upscaling_app.commands.common import (
    add_ssdi_source_argument,
)


def _run_ssmd_reference(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssmd.reporting import (
        print_reference_report,
    )
    from upscaling_app.upscaling.ssmd.workflows.reference import (
        run_reference,
    )

    predictions = run_reference(
        ssdi_source_version=args.ssdi_source_version,
    )

    print_reference_report(
        predictions,
    )


def _run_ssmd_global(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssmd.reporting import (
        print_global_report,
    )
    from upscaling_app.upscaling.ssmd.workflows.global_cd import (
        run_global,
    )

    predictions = run_global(
        ssdi_source_version=args.ssdi_source_version,
    )

    print_global_report(
        predictions,
    )


def _run_ssmd_oil_wise(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssmd.reporting import (
        print_oil_wise_report,
    )
    from upscaling_app.upscaling.ssmd.workflows.oil_wise import (
        run_oil_wise,
    )

    predictions = run_oil_wise(
        ssdi_source_version=args.ssdi_source_version,
    )

    print_oil_wise_report(
        predictions,
    )


def _run_ssmd_performance(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssmd.performance.pipeline import (
        run_ssmd_performance_workflow,
    )

    run_ssmd_performance_workflow(
        ssdi_source_version=args.ssdi_source_version,
    )


def _run_ssmd_oil_wise_analysis(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssmd.oil_wise.pipeline import (
        run_ssmd_oil_wise_workflow,
    )

    run_ssmd_oil_wise_workflow(
        ssdi_source_version=args.ssdi_source_version,
    )


def _run_ssmd_validation(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssmd.validation.pipeline import (
        run_ssmd_validation_workflow,
    )

    run_ssmd_validation_workflow(
        ssdi_source_version=args.ssdi_source_version,
    )


def register_ssmd_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    ssmd_parser = subparsers.add_parser(
        "ssmd",
        help="Run SSMD modelling workflows.",
    )

    commands = ssmd_parser.add_subparsers(
        dest="ssmd_command",
        required=True,
    )

    reference_parser = commands.add_parser(
        "reference",
        help="Run the reconstructed SINTEF SSMD reference.",
    )

    add_ssdi_source_argument(
        reference_parser,
    )

    reference_parser.set_defaults(
        handler=_run_ssmd_reference,
    )

    global_parser = commands.add_parser(
        "global",
        help="Fit and run the global SSMD c,d model.",
    )

    add_ssdi_source_argument(
        global_parser,
    )

    global_parser.set_defaults(
        handler=_run_ssmd_global,
    )

    oil_wise_parser = commands.add_parser(
        "oil-wise",
        help="Fit and run the oil-wise SSMD factor model.",
    )

    add_ssdi_source_argument(
        oil_wise_parser,
    )

    oil_wise_parser.set_defaults(
        handler=_run_ssmd_oil_wise,
    )


def register_ssmd_analysis_commands(
    analysis_subparsers: argparse._SubParsersAction,
) -> None:
    ssmd_parser = analysis_subparsers.add_parser(
        "ssmd",
        help="Analyze SSMD model results.",
    )

    commands = ssmd_parser.add_subparsers(
        dest="ssmd_analysis_command",
        required=True,
    )

    performance_parser = commands.add_parser(
        "performance",
        help="Compare SSMD reference and global model performance.",
    )

    add_ssdi_source_argument(
        performance_parser,
    )

    performance_parser.set_defaults(
        handler=_run_ssmd_performance,
    )

    oil_wise_parser = commands.add_parser(
        "oil-wise",
        help="Analyze oil-wise SSMD factor heterogeneity.",
    )

    add_ssdi_source_argument(
        oil_wise_parser,
    )

    oil_wise_parser.set_defaults(
        handler=_run_ssmd_oil_wise_analysis,
    )

    validation_parser = commands.add_parser(
        "validation",
        help=(
            "Run leave-one-oil-out predictive validation "
            "for the global SSMD c,d model."
        ),
    )

    add_ssdi_source_argument(
        validation_parser,
    )

    validation_parser.set_defaults(
        handler=_run_ssmd_validation,
    )
