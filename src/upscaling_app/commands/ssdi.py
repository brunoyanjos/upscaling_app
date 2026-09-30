from __future__ import annotations

import argparse


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

    print_baseline_report(
        result,
    )


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


def register_ssdi_commands(
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


def register_ssdi_analysis_commands(
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
        help="Recalibrate after excluding baseline IQR residual outliers.",
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

    oil_wise_parser = commands.add_parser(
        "oil-wise",
        help="Compare global and oil-wise SSDI calibrations.",
    )

    oil_wise_parser.set_defaults(
        handler=_run_ssdi_oil_wise_analysis,
    )

    comparison_parser = commands.add_parser(
        "compare",
        help="Compare SSDI model versions.",
    )

    comparison_parser.set_defaults(
        handler=_run_ssdi_comparison,
    )

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
