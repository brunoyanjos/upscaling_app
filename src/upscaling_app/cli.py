from __future__ import annotations

import argparse
import os
from pathlib import Path


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="upscaling",
        description="Upscaling application for oil dispersion modelling.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # =========================================================
    # Database
    # =========================================================

    database_parser = subparsers.add_parser(
        "database",
        help="Database operations.",
    )

    database_subparsers = database_parser.add_subparsers(
        dest="database_command",
        required=True,
    )

    database_subparsers.add_parser(
        "build",
        help="Build databases from raw data.",
    )

    # =========================================================
    # SSDI
    # =========================================================

    ssdi_parser = subparsers.add_parser(
        "ssdi",
        help="Run SSDI modelling workflows.",
    )

    ssdi_subparsers = ssdi_parser.add_subparsers(
        dest="ssdi_command",
    )

    ssdi_subparsers.add_parser(
        "baseline",
        help="Run the SSDI baseline calibration.",
    )

    ssdi_subparsers.add_parser(
        "filtered",
        help="Run the SSDI calibration excluding baseline IQR outliers.",
    )

    ssdi_subparsers.add_parser(
        "oil-sensitivity",
        help="Run SSDI sensitivity analysis excluding oils 3016 and 4665.",
    )

    # =========================================================
    # SSMD
    # =========================================================

    ssmd_parser = subparsers.add_parser(
        "ssmd",
        help="Run SSMD modelling workflows.",
    )

    ssmd_subparsers = ssmd_parser.add_subparsers(
        dest="ssmd_command",
    )

    ssmd_subparsers.add_parser(
        "baseline",
        help="Run the baseline SSMD workflow.",
    )

    # =========================================================
    # Distribution
    # =========================================================

    distribution_parser = subparsers.add_parser(
        "distribution",
    )

    distribution_parser.add_argument(
        "--config",
        type=Path,
        required=True,
    )

    # =========================================================
    # Analysis
    # =========================================================

    analysis_parser = subparsers.add_parser(
        "analyze",
        help="Run statistical analyses.",
    )

    analysis_subparsers = analysis_parser.add_subparsers(
        dest="analysis_command",
        required=True,
    )

    # ---------------------------------------------------------
    # SSDI analysis
    # ---------------------------------------------------------

    ssdi_analysis_parser = analysis_subparsers.add_parser(
        "ssdi",
        help="Analyze SSDI model results.",
    )

    ssdi_analysis_group = ssdi_analysis_parser.add_mutually_exclusive_group()

    ssdi_analysis_group.add_argument(
        "--model",
        choices=[
            "baseline",
            "filtered",
            "reference",
            "oil-sensitivity",
        ],
        default=None,
        help="SSDI model version to analyze.",
    )

    ssdi_analysis_group.add_argument(
        "--compare",
        action="store_true",
        help="Compare SSDI calibration strategies.",
    )

    ssdi_analysis_group.add_argument(
        "--loo",
        action="store_true",
        help="Run leave-one-oil-out validation.",
    )

    # ---------------------------------------------------------
    # SSMD analysis
    # ---------------------------------------------------------

    ssmd_analysis_parser = analysis_subparsers.add_parser(
        "ssmd",
        help="Analyze SSMD model results.",
    )

    ssmd_analysis_parser.add_argument(
        "--loo",
        action="store_true",
        help="Run leave-one-oil-out validation.",
    )

    # ---------------------------------------------------------
    # Experimental analysis
    # ---------------------------------------------------------

    experimental_analysis_parser = analysis_subparsers.add_parser(
        "experimental",
        help="Analyze experimental data.",
    )

    experimental_subparsers = experimental_analysis_parser.add_subparsers(
        dest="experimental_command",
        required=True,
    )

    experimental_subparsers.add_parser(
        "descriptive",
        help="Run descriptive experimental analysis.",
    )

    experimental_subparsers.add_parser(
        "ssdi",
        help="Analyze SSDI experimental relationships.",
    )

    experimental_subparsers.add_parser(
        "ssmd",
        help="Analyze SSMD experimental relationships.",
    )

    experimental_subparsers.add_parser(
        "treatment-effect",
        help="Analyze measured d50 reduction relative to untreated conditions.",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    # =========================================================
    # Runtime configuration
    # =========================================================

    if args.command == "ssdi" or (
        args.command == "analyze" and args.analysis_command == "ssdi"
    ):
        os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

    # =========================================================
    # Database
    # =========================================================

    if args.command == "database":
        if args.database_command == "build":
            from upscaling_app.database.build import build_database

            build_database()

    # =========================================================
    # SSDI
    # =========================================================

    elif args.command == "ssdi":
        if args.ssdi_command in (None, "baseline"):
            from upscaling_app.upscaling.ssdi.reporting import (
                print_baseline_report,
            )
            from upscaling_app.upscaling.ssdi.workflows.baseline import (
                run_baseline,
            )

            result = run_baseline()

            print_baseline_report(result)

        elif args.ssdi_command == "filtered":
            from upscaling_app.upscaling.ssdi.reporting import (
                print_filtered_report,
            )
            from upscaling_app.upscaling.ssdi.workflows.filtered import (
                run_filtered,
            )

            result = run_filtered()

            print_filtered_report(result)

        elif args.ssdi_command == "oil-sensitivity":
            from upscaling_app.upscaling.ssdi.reporting import (
                print_model_report,
            )
            from upscaling_app.upscaling.ssdi.workflows.oil_sensitivity import (
                run_oil_sensitivity,
            )

            result = run_oil_sensitivity()

            print_model_report(
                result=result,
                title="SSDI OIL SENSITIVITY CALIBRATION",
            )

    # =========================================================
    # SSMD
    # =========================================================

    elif args.command == "ssmd":
        if args.ssmd_command in (None, "baseline"):
            from upscaling_app.upscaling.ssmd.reporting import (
                print_baseline_report,
            )
            from upscaling_app.upscaling.ssmd.workflows.baseline import (
                run_baseline,
            )

            result = run_baseline()

            print_baseline_report(result)

    # =========================================================
    # Analysis
    # =========================================================

    elif args.command == "analyze":

        # -----------------------------------------------------
        # SSDI analysis
        # -----------------------------------------------------

        if args.analysis_command == "ssdi":

            # Leave-one-oil-out validation

            if args.loo:
                from upscaling_app.analysis.ssdi.evaluation.comparison import (
                    build_evaluation_comparison,
                )
                from upscaling_app.analysis.ssdi.evaluation.leave_one_oil_out import (
                    run_leave_one_oil_out,
                )
                from upscaling_app.analysis.ssdi.io.persistence import (
                    save_evaluation_comparison,
                    save_leave_one_oil_out,
                )
                from upscaling_app.analysis.ssdi.plotting import (
                    save_leave_one_oil_out_bias_plot,
                    save_leave_one_oil_out_mape_plot,
                    save_leave_one_oil_out_plot,
                )
                from upscaling_app.analysis.ssdi.reporting import (
                    print_evaluation_comparison,
                    print_leave_one_oil_out_report,
                )

                result = run_leave_one_oil_out()

                save_leave_one_oil_out(result)

                save_leave_one_oil_out_plot(result.folds)
                save_leave_one_oil_out_mape_plot(result.folds)
                save_leave_one_oil_out_bias_plot(result.folds)

                comparison = build_evaluation_comparison(result)

                save_evaluation_comparison(comparison)

                print_leave_one_oil_out_report(result)
                print_evaluation_comparison(comparison)

                return

            # Model comparison

            if args.compare:
                from upscaling_app.analysis.ssdi.evaluation.comparison import (
                    build_model_comparison,
                )
                from upscaling_app.analysis.ssdi.io.persistence import (
                    save_model_comparison,
                )
                from upscaling_app.analysis.ssdi.reporting import (
                    print_model_comparison,
                )

                comparison = build_model_comparison()

                save_model_comparison(comparison)
                print_model_comparison(comparison)

                return

            # Individual model analysis

            from upscaling_app.analysis.ssdi.pipeline import (
                run_ssdi_analysis,
            )
            from upscaling_app.analysis.ssdi.reporting import (
                print_ssdi_analysis_report,
            )
            from upscaling_app.upscaling.ssdi.versions import (
                BASELINE_VERSION,
                FILTERED_VERSION,
                OIL_SENSITIVITY_VERSION,
                REFERENCE_VERSION,
            )

            model_versions = {
                "baseline": BASELINE_VERSION,
                "filtered": FILTERED_VERSION,
                "reference": REFERENCE_VERSION,
                "oil-sensitivity": OIL_SENSITIVITY_VERSION,
            }

            model_name = args.model or "baseline"
            model_version = model_versions[model_name]

            results, metrics = run_ssdi_analysis(
                model_version=model_version,
            )

            print_ssdi_analysis_report(
                results=results,
                metrics=metrics,
                model_version=model_version,
            )

        # -----------------------------------------------------
        # SSMD analysis
        # -----------------------------------------------------

        elif args.analysis_command == "ssmd":

            if args.loo:

                return

            from upscaling_app.analysis.ssmd.pipeline import (
                run_ssmd_analysis,
            )

            run_ssmd_analysis()

        # ============================================================
        # Experimental analysis
        # ============================================================

        elif args.analysis_command == "experimental":

            if args.experimental_command == "summary":
                from upscaling_app.analysis.experimental.pipeline import (
                    run_experimental_analysis,
                )
                from upscaling_app.analysis.experimental.reporting import (
                    print_experimental_analysis_report,
                )

                result = run_experimental_analysis(
                    kind=args.kind,
                )

                print_experimental_analysis_report(result)

            elif args.experimental_command == "ssdi":
                from upscaling_app.analysis.experimental.pipeline import (
                    run_ssdi_experimental_analysis,
                )
                from upscaling_app.analysis.experimental.reporting import (
                    print_ssdi_experimental_report,
                )

                result = run_ssdi_experimental_analysis()

                print_ssdi_experimental_report(result)

            elif args.experimental_command == "ssmd":
                from upscaling_app.analysis.experimental.pipeline import (
                    run_ssmd_experimental_analysis,
                )
                from upscaling_app.analysis.experimental.reporting import (
                    print_ssmd_experimental_report,
                )

                result = run_ssmd_experimental_analysis()

                print_ssmd_experimental_report(result)

            elif args.experimental_command == "treatment-effect":
                from upscaling_app.analysis.experimental.pipeline import (
                    run_treatment_effect_analysis,
                )
                from upscaling_app.analysis.experimental.reporting import (
                    print_treatment_effect_report,
                )

                result = run_treatment_effect_analysis()

                print_treatment_effect_report(result)


if __name__ == "__main__":
    main()
