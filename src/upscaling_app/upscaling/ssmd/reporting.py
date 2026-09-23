from __future__ import annotations

from upscaling_app.upscaling.ssmd.results import (
    BaselineResult,
    SSMDModelResult,
    SSMDRegimeResult,
)


def _regime_name(
    regime: SSMDRegimeResult,
) -> str:
    diameter_mm = regime.nozzle_diameter * 1e3

    if regime.has_gas:
        return f"{diameter_mm:.0f} mm + gas"

    return f"{diameter_mm:.0f} mm"


def _print_regimes(
    result: SSMDModelResult,
) -> None:
    for regime in result.regimes:
        print(f"\n{_regime_name(regime)}")
        print(f"  eta                : {regime.eta:.6f}")
        print(f"  c                  : {regime.c_coef:.6f}")
        print(f"  d                  : {regime.d_coef:.6f}")


def _print_global_coefficients(
    result: SSMDModelResult,
) -> None:
    first_regime = result.regimes[0]

    print(f"  c                  : {first_regime.c_coef:.6f}")
    print(f"  d                  : {first_regime.d_coef:.6f}")


def print_baseline_report(
    result: BaselineResult,
) -> None:
    model = result.model
    global_model = result.global_model
    reference = result.reference

    regime_reduction = (reference.loss - model.loss) / reference.loss * 100.0

    global_reduction = (reference.loss - global_model.loss) / reference.loss * 100.0

    print("\n" + "=" * 60)
    print("SSMD BASELINE CALIBRATION")
    print("=" * 60)

    print("\nDataset")
    print(f"  Experiments        : {model.experiment_count}")

    print("\nRegressed by regime")
    _print_regimes(model)
    print(f"\n  Log-MSE            : {model.loss:.6f}")

    print("\nGlobal regression")
    _print_global_coefficients(global_model)
    print(f"  Log-MSE            : {global_model.loss:.6f}")

    print("\nSINTEF reference")
    _print_regimes(reference)
    print(f"\n  Log-MSE            : {reference.loss:.6f}")

    print("\nComparison")
    print(f"  By-regime reduction: {regime_reduction:.2f} %")
    print(f"  Global reduction   : {global_reduction:.2f} %")

    print("\nStatus: completed")
    print("=" * 60)
