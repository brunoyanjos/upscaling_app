from __future__ import annotations

import argparse
import os
from importlib.metadata import PackageNotFoundError, version

import argcomplete


def _package_version() -> str:
    try:
        return version("upscaling-app")
    except PackageNotFoundError:
        return "0.1.0"


# ============================================================
# Database handlers
# ============================================================


def _run_database_build(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.database.build import build_database

    build_database()


# ============================================================
# SSDI modelling handlers
# ============================================================


def _run_ssdi_baseline(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssdi.reporting import (
        print_baseline_report,
    )
    from upscaling_app.upscaling.ssdi.workflows.baseline import (
        run_baseline,
    )

    result = run_baseline()

    print_baseline_report(result)


def _run_ssdi_oil_wise(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssdi.reporting import (
        print_oil_wise_report,
    )
    from upscaling_app.upscaling.ssdi.workflows.oil_wise import (
        run_oil_wise,
    )

    calibrations = run_oil_wise()

    print_oil_wise_report(
        calibrations,
    )


# ============================================================
# SSMD modelling handlers
# ============================================================


def _run_ssmd_baseline(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.upscaling.ssmd.reporting import (
        print_baseline_report,
    )
    from upscaling_app.upscaling.ssmd.workflows.baseline import (
        run_baseline,
    )

    result = run_baseline()

    print_baseline_report(result)


# ============================================================
# Experimental-analysis handlers
# ============================================================


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


# ============================================================
# SSDI-analysis handlers
# ============================================================


def _run_ssdi_performance(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.performance.pipeline import (
        run_ssdi_performance_workflow,
    )
    from upscaling_app.upscaling.ssdi.versions import (
        BASELINE_VERSION,
        REFERENCE_VERSION,
    )

    models = {
        "baseline": {
            "version": BASELINE_VERSION,
            "label": "Global calibration",
            "figure": "baseline_parity.png",
        },
        "reference": {
            "version": REFERENCE_VERSION,
            "label": "SINTEF reference",
            "figure": "reference_parity.png",
        },
    }

    model = models[args.model]

    run_ssdi_performance_workflow(
        model_version=model["version"],
        model_label=model["label"],
        figure_name=model["figure"],
    )


def _run_ssdi_iqr_sensitivity(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.sensitivity.pipeline import (
        run_iqr_sensitivity_workflow,
    )

    run_iqr_sensitivity_workflow()


def _run_ssdi_oil_residual_sensitivity(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.sensitivity.pipeline import (
        run_oil_residual_sensitivity_workflow,
    )

    run_oil_residual_sensitivity_workflow()


def _run_ssdi_oil_extended_sensitivity(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.sensitivity.pipeline import (
        run_oil_extended_sensitivity_workflow,
    )

    run_oil_extended_sensitivity_workflow()


def _run_ssdi_oil_wise_analysis(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.oil_wise.pipeline import (
        run_oil_wise_comparison_workflow,
    )

    run_oil_wise_comparison_workflow()


def _run_ssdi_comparison(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.comparison.pipeline import (
        run_ssdi_model_comparison_workflow,
    )

    run_ssdi_model_comparison_workflow()


def _run_ssdi_loo_all(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.validation.pipeline import (
        run_loo_all_workflow,
    )

    run_loo_all_workflow()


def _run_ssdi_loo_retained(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.validation.pipeline import (
        run_loo_retained_workflow,
    )

    run_loo_retained_workflow()


def _run_ssdi_excluded_challenge(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.validation.pipeline import (
        run_excluded_challenge_workflow,
    )

    run_excluded_challenge_workflow()


def _run_ssdi_validation_comparison(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssdi.validation.pipeline import (
        run_validation_comparison_workflow,
    )

    run_validation_comparison_workflow()


# ============================================================
# SSMD-analysis handlers
# ============================================================


def _run_ssmd_performance(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.ssmd.pipeline import (
        run_ssmd_analysis,
    )

    run_ssmd_analysis()


# ============================================================
# Distribution-analysis handlers
# ============================================================


def _run_distribution_analysis(
    args: argparse.Namespace,
) -> None:
    from upscaling_app.analysis.distributions.pipeline import (
        run_distribution_analysis,
    )
    from upscaling_app.analysis.distributions.reporting import (
        print_distribution_analysis_report,
    )

    result = run_distribution_analysis()

    print_distribution_analysis_report(result)


# ============================================================
# Parser configuration
# ============================================================


def _add_database_commands(
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


def _add_ssdi_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    ssdi_parser = subparsers.add_parser(
        "ssdi",
        help="Run SSDI modelling workflows.",
    )

    commands = ssdi_parser.add_subparsers(
        dest="ssdi_command",
        required=True,
    )

    baseline_parser = commands.add_parser(
        "baseline",
        help="Run global SSDI baseline calibration.",
    )

    baseline_parser.set_defaults(
        handler=_run_ssdi_baseline,
    )

    oil_wise_parser = commands.add_parser(
        "oil-wise",
        help="Run independent SSDI calibration for each oil.",
    )

    oil_wise_parser.set_defaults(
        handler=_run_ssdi_oil_wise,
    )


def _add_ssmd_commands(
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

    baseline_parser = commands.add_parser(
        "baseline",
        help="Run the SSMD baseline workflow.",
    )

    baseline_parser.set_defaults(
        handler=_run_ssmd_baseline,
    )


def _add_experimental_analysis_commands(
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


def _add_ssdi_analysis_commands(
    analysis_subparsers: argparse._SubParsersAction,
) -> None:
    ssdi_parser = analysis_subparsers.add_parser(
        "ssdi",
        help="Analyze SSDI model results.",
    )

    commands = ssdi_parser.add_subparsers(
        dest="ssdi_analysis_command",
        required=True,
    )

    # --------------------------------------------------------
    # Performance
    # --------------------------------------------------------

    performance_parser = commands.add_parser(
        "performance",
        help="Evaluate persisted SSDI predictions.",
    )

    performance_commands = performance_parser.add_subparsers(
        dest="ssdi_performance_model",
        required=True,
    )

    baseline_parser = performance_commands.add_parser(
        "baseline",
        help="Evaluate the calibrated global SSDI baseline.",
    )

    baseline_parser.set_defaults(
        handler=_run_ssdi_performance,
        model="baseline",
    )

    reference_parser = performance_commands.add_parser(
        "reference",
        help="Evaluate the SINTEF SSDI reference coefficients.",
    )

    reference_parser.set_defaults(
        handler=_run_ssdi_performance,
        model="reference",
    )

    # --------------------------------------------------------
    # Sensitivity
    # --------------------------------------------------------

    sensitivity_parser = commands.add_parser(
        "sensitivity",
        help="Run SSDI calibration-sensitivity studies.",
    )

    sensitivity_commands = sensitivity_parser.add_subparsers(
        dest="ssdi_sensitivity_command",
        required=True,
    )

    iqr_parser = sensitivity_commands.add_parser(
        "iqr",
        help=("Recalibrate after excluding baseline " "IQR residual outliers."),
    )

    iqr_parser.set_defaults(
        handler=_run_ssdi_iqr_sensitivity,
    )

    oil_residual_parser = sensitivity_commands.add_parser(
        "oil-residual",
        help=(
            "Recalibrate after excluding oils associated "
            "with the strongest baseline residual anomalies."
        ),
    )

    oil_residual_parser.set_defaults(
        handler=_run_ssdi_oil_residual_sensitivity,
    )

    oil_extended_parser = sensitivity_commands.add_parser(
        "oil-extended",
        help=("Recalibrate using the extended set of " "diagnostically atypical oils."),
    )

    oil_extended_parser.set_defaults(
        handler=_run_ssdi_oil_extended_sensitivity,
    )

    # --------------------------------------------------------
    # Oil-wise
    # --------------------------------------------------------

    oil_wise_parser = commands.add_parser(
        "oil-wise",
        help="Compare global and oil-wise SSDI calibrations.",
    )

    oil_wise_parser.set_defaults(
        handler=_run_ssdi_oil_wise_analysis,
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    comparison_parser = commands.add_parser(
        "compare",
        help="Compare SSDI model versions.",
    )

    comparison_parser.set_defaults(
        handler=_run_ssdi_comparison,
    )

    # --------------------------------------------------------
    # Predictive validation
    # --------------------------------------------------------

    validation_parser = commands.add_parser(
        "validation",
        help="Run SSDI predictive-validation workflows.",
    )

    validation_commands = validation_parser.add_subparsers(
        dest="ssdi_validation_command",
        required=True,
    )

    loo_all_parser = validation_commands.add_parser(
        "loo-all",
        help=(
            "Run leave-one-oil-out validation " "over the complete SSDI oil population."
        ),
    )

    loo_all_parser.set_defaults(
        handler=_run_ssdi_loo_all,
    )

    loo_retained_parser = validation_commands.add_parser(
        "loo-retained",
        help=(
            "Run leave-one-oil-out validation " "over the retained SSDI oil population."
        ),
    )

    loo_retained_parser.set_defaults(
        handler=_run_ssdi_loo_retained,
    )

    challenge_parser = validation_commands.add_parser(
        "excluded-challenge",
        help=(
            "Calibrate on retained oils and evaluate "
            "the diagnostically excluded oils."
        ),
    )

    challenge_parser.set_defaults(
        handler=_run_ssdi_excluded_challenge,
    )

    comparison_parser = validation_commands.add_parser(
        "compare",
        help=(
            "Compare complete-population LOO, retained-population "
            "LOO, and the excluded-oil challenge."
        ),
    )

    comparison_parser.set_defaults(
        handler=_run_ssdi_validation_comparison,
    )


def _add_ssmd_analysis_commands(
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
        help="Evaluate persisted SSMD predictions.",
    )

    performance_parser.set_defaults(
        handler=_run_ssmd_performance,
    )


def _add_analysis_commands(
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

    _add_experimental_analysis_commands(commands)
    _add_ssdi_analysis_commands(commands)
    _add_ssmd_analysis_commands(commands)

    distributions_parser = commands.add_parser(
        "distributions",
        help="Analyze measured droplet-size distributions.",
    )

    distributions_parser.set_defaults(
        handler=_run_distribution_analysis,
    )


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

    _add_database_commands(subparsers)
    _add_ssdi_commands(subparsers)
    _add_ssmd_commands(subparsers)
    _add_analysis_commands(subparsers)

    return parser


def main() -> None:
    parser = create_parser()

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    os.environ.setdefault(
        "XLA_PYTHON_CLIENT_PREALLOCATE",
        "false",
    )

    args.handler(args)


if __name__ == "__main__":
    main()
